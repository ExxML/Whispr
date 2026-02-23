import ctypes
import ctypes.wintypes
import math
import threading

from PyQt6.QtCore import QObject, QPoint, QTimer, pyqtSignal
from PyQt6.QtWidgets import QApplication

from core.win32_hook import (
    HOOKPROC,
    KBDLLHOOKSTRUCT,
    MOD_ALT,
    MOD_CTRL,
    MOD_SHIFT,
    MODIFIER_VK_CODES,
    VK_DOWN,
    VK_LEFT,
    VK_RIGHT,
    VK_UP,
    WH_KEYBOARD_LL,
    WM_KEYDOWN,
    WM_KEYUP,
    WM_QUIT,
    WM_SYSKEYDOWN,
    WM_SYSKEYUP,
    get_active_modifiers,
    kernel32,
    user32,
)


class ShortcutManager(QObject):
    """Manages global keyboard shortcuts via a Win32 low-level keyboard hook.
    
    All registered hotkeys are suppressed so other applications never see the
    key events. Conditional hotkeys (everything except the visibility toggle)
    are only active while the main window is visible.
    """

    # Qt signals for thread-safe communication with the main thread
    # ALL UI actions must be performed on the main thread to avoid crashes and unpredictable behaviour (ex. leaking hotkeys)
    move_signal = pyqtSignal(int, int)
    scroll_signal = pyqtSignal(int)
    quit_signal = pyqtSignal()
    screenshot_signal = pyqtSignal()
    clear_chat_signal = pyqtSignal()
    minimize_signal = pyqtSignal()
    toggle_signal = pyqtSignal()
    generate_content_with_screenshot_signal = pyqtSignal(str, bool)

    def __init__(self, main_window, screenshot_manager):
        super().__init__()
        self.main_window = main_window
        self.screenshot_manager = screenshot_manager

        # Connect signals
        self.move_signal.connect(self._start_animation)  # Signal needed because QTimers cannot be started from another thread
        self.scroll_signal.connect(self.main_window.chat_area.shortcut_scroll)
        self.quit_signal.connect(self.main_window.quit_app)
        self.screenshot_signal.connect(self.screenshot_manager.take_screenshot)
        self.clear_chat_signal.connect(self.main_window.chat_area.clear_chat)
        self.minimize_signal.connect(self.main_window.hide)
        self.toggle_signal.connect(self.main_window.toggle_window_visibility)
        self.generate_content_with_screenshot_signal.connect(self.main_window.worker.handle_message)

        # Initialize animation
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animate_step)
        self.animation_active = False
        self.animation_start_pos = None
        self.animation_target_pos = None
        self.animation_progress = 0.0
        self.setup_movement_distances()

        # Hotkey lookup tables: (modifier_bitmask, vk_code) -> (callback, repeat_callbacks)
        self._always_active_hotkeys: dict[tuple[int, int], tuple[callable, bool]] = {}
        self._main_window_hotkeys: dict[tuple[int, int], tuple[callable, bool]] = {}
        self._suppressed_vk_codes: set[int] = set()
        self._held_vk_codes: set[int] = set()  # Tracks physically held non-modifier keys
        self._define_hotkeys()

        # Low-level keyboard hook (prevent GC of the callback reference)
        self._hook_proc_ref = HOOKPROC(self._low_level_keyboard_proc)
        self._hook_handle = None
        self._hook_thread_id = None
        self._start_hook()

    # Hotkey Definitions

    def _define_hotkeys(self):
        """Populate the hotkey lookup tables.

        Default Shortcuts:
            Ctrl + E - Show / hide main window (always active)
            Ctrl + D - Generate AI output (trigger on release)
            Ctrl + G - Fix / improve code (trigger on release)
            Ctrl + Alt + <ArrowKeys> - Move main window
            Ctrl + Shift + Up / Down - Scroll chat area
            Ctrl + Shift + Q - Quit the application
            Ctrl + Shift + C - Take a screenshot
            Ctrl + Q - Minimize main window
            Ctrl + N - Clear chat history
        """
        self._always_active_hotkeys = {
            (MOD_CTRL, ord("E")): (self.toggle_window_visibility, False),
            (MOD_CTRL | MOD_SHIFT, ord("Q")): (self.close_app, False),
        }

        self._main_window_hotkeys = {
            (MOD_CTRL | MOD_ALT, VK_LEFT): (self.move_window_left, True),
            (MOD_CTRL | MOD_ALT, VK_RIGHT): (self.move_window_right, True),
            (MOD_CTRL | MOD_ALT, VK_UP): (self.move_window_up, True),
            (MOD_CTRL | MOD_ALT, VK_DOWN): (self.move_window_down, True),
            (MOD_CTRL | MOD_SHIFT, VK_UP): (self.scroll_up, True),
            (MOD_CTRL | MOD_SHIFT, VK_DOWN): (self.scroll_down, True),
            (MOD_CTRL | MOD_SHIFT, ord("C")): (self.screenshot, False),
            (MOD_CTRL, ord("Q")): (self.minimize, False),
            (MOD_CTRL, ord("N")): (self.clear_chat, False),
            (MOD_CTRL, ord("D")): (self.generate_with_screenshot, False),
            (MOD_CTRL, ord("G")): (self.generate_with_screenshot_fix, False),
        }

    # Win32 Keyboard Hook Logic

    def _low_level_keyboard_proc(self, nCode, wParam, lParam):
        """Win32 low-level keyboard hook callback.

        Checks every key event against the registered hotkey tables.
        Matching events are suppressed (not forwarded to other applications).

        Args:
            nCode (int): Hook code indicating how to process the message.
            wParam (int): Message type identifier (e.g. WM_KEYDOWN, WM_KEYUP).
            lParam (int): Pointer to a KBDLLHOOKSTRUCT containing key event data.

        Returns:
            int: 1 to suppress the key event, or the result of CallNextHookEx.
        """
        if nCode >= 0:
            kb = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
            vk_code = kb.vkCode
            is_key_down = wParam in (WM_KEYDOWN, WM_SYSKEYDOWN)
            is_key_up = wParam in (WM_KEYUP, WM_SYSKEYUP)

            # Only match on non-modifier keys; modifiers are always passed through
            if vk_code not in MODIFIER_VK_CODES:
                modifiers = get_active_modifiers()
                hotkey_key = (modifiers, vk_code)

                # Look up in always-active table first, then main window table
                entry = self._always_active_hotkeys.get(hotkey_key)
                if entry is None and self.main_window.isVisible():
                    entry = self._main_window_hotkeys.get(hotkey_key)

                if entry is not None:
                    callback, repeat_callbacks = entry
                    if is_key_down:
                        # For no-repeat hotkeys, skip if the key is already physically held
                        if not repeat_callbacks and vk_code in self._held_vk_codes:
                            return 1  # Suppress repeat without calling callback
                        self._held_vk_codes.add(vk_code)
                        self._suppressed_vk_codes.add(vk_code)
                        callback()
                        return 1  # Suppress the key event

                    if is_key_up:
                        self._held_vk_codes.discard(vk_code)
                        if vk_code in self._suppressed_vk_codes:
                            self._suppressed_vk_codes.discard(vk_code)
                            return 1  # Suppress the matching key-up

                elif is_key_up:
                    # Key was held but hotkey no longer matches (e.g. modifier released early) - clean up
                    self._held_vk_codes.discard(vk_code)
                    if vk_code in self._suppressed_vk_codes:
                        self._suppressed_vk_codes.discard(vk_code)
                        return 1  # Suppress key-up even though modifiers changed

        return user32.CallNextHookEx(self._hook_handle, nCode, wParam, lParam)

    def _hook_thread_entry(self):
        """Entry point for the keyboard hook thread.

        Installs the low-level keyboard hook, then enters a message loop that
        keeps the hook alive until a WM_QUIT message is posted.
        """
        self._hook_thread_id = kernel32.GetCurrentThreadId()
        h_module = kernel32.GetModuleHandleW(None)

        self._hook_handle = user32.SetWindowsHookExW(
            WH_KEYBOARD_LL,
            self._hook_proc_ref,
            h_module,
            0,  # Monitor all threads (required for low-level hooks)
        )

        # Pump messages to keep the hook alive
        msg = ctypes.wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            pass  # No dispatch needed; WM_QUIT causes GetMessageW to return 0

        if self._hook_handle:
            user32.UnhookWindowsHookEx(self._hook_handle)
            self._hook_handle = None

    def _start_hook(self):
        """Start the keyboard hook on a dedicated daemon thread"""
        thread = threading.Thread(target=self._hook_thread_entry, daemon=True)
        thread.start()

    def stop_hook(self):
        """Stop the keyboard hook and its message loop"""
        if self._hook_thread_id is not None:
            user32.PostThreadMessageW(self._hook_thread_id, WM_QUIT, 0, 0)
            self._hook_thread_id = None

    # Hotkey Callback Functions

    def toggle_window_visibility(self):
        """Toggle main window visibility"""
        self.toggle_signal.emit()

    def setup_movement_distances(self):
        """Determine screen geometry and movement distances"""
        self.screen_rect = QApplication.primaryScreen().availableGeometry()
        self.max_move_distance_x = self.screen_rect.width() // 14
        self.max_move_distance_y = self.screen_rect.height() // 14
        self.screen_bounds_offset = 2  # Always keep 2 pixels to screen edge to prevent setGeometry errors
        self.animation_duration = 100  # Animation duration in milliseconds
        self.animation_fps = 120  # Frames per second
        self.animation_frame_time = 1000 // self.animation_fps  # Time per frame in ms

    def _start_animation(self, target_x, target_y):
        """Begin an animated move to the target position.

        Args:
            target_x (int): Target x-coordinate for the main window.
            target_y (int): Target y-coordinate for the main window.
        """
        self.animation_start_pos = self.main_window.pos()
        self.animation_target_pos = QPoint(target_x, target_y)
        self.animation_progress = 0.0
        self.animation_active = True
        self.animation_timer.start(self.animation_frame_time)

    def _animate_step(self):
        """Advance one frame of the movement animation"""
        self.animation_progress += self.animation_frame_time / self.animation_duration

        if self.animation_progress >= 1.0:
            # Animation complete
            self.main_window.move(self.animation_target_pos)
            self.animation_timer.stop()
            self.animation_active = False
        else:
            # Ease-out sine motion: sin(t * π/2)
            ease_progress = math.sin(self.animation_progress * math.pi / 2)
            current_x = int(self.animation_start_pos.x() + (self.animation_target_pos.x() - self.animation_start_pos.x()) * ease_progress)
            current_y = int(self.animation_start_pos.y() + (self.animation_target_pos.y() - self.animation_start_pos.y()) * ease_progress)
            self.main_window.move(current_x, current_y)

    def move_window_left(self):
        """Move main window left"""
        if self.animation_active and self.animation_progress < 0.5:
            return
        new_x = max(self.screen_bounds_offset, self.main_window.geometry().x() - self.max_move_distance_x)
        self.move_signal.emit(new_x, self.main_window.geometry().y())

    def move_window_right(self):
        """Move main window right"""
        if self.animation_active and self.animation_progress < 0.5:
            return
        max_x = self.screen_rect.width() - self.main_window.geometry().width() - self.screen_bounds_offset
        new_x = min(max_x, self.main_window.geometry().x() + self.max_move_distance_x)
        self.move_signal.emit(new_x, self.main_window.geometry().y())

    def move_window_up(self):
        """Move main window up"""
        if self.animation_active and self.animation_progress < 0.5:
            return
        new_y = max(self.screen_bounds_offset, self.main_window.geometry().y() - self.max_move_distance_y)
        self.move_signal.emit(self.main_window.geometry().x(), new_y)

    def move_window_down(self):
        """Move main window down"""
        if self.animation_active and self.animation_progress < 0.5:
            return
        max_y = self.screen_rect.height() - self.main_window.geometry().height() - self.screen_bounds_offset
        new_y = min(max_y, self.main_window.geometry().y() + self.max_move_distance_y)
        self.move_signal.emit(self.main_window.geometry().x(), new_y)

    def scroll_up(self):
        """Scroll up in the chat area"""
        self.scroll_signal.emit(-100)

    def scroll_down(self):
        """Scroll down in the chat area"""
        self.scroll_signal.emit(100)

    def close_app(self):
        """Close the application"""
        self.quit_signal.emit()  # Must emit signal to run on main thread

    def screenshot(self):
        """Take a screenshot of the primary screen"""
        self.screenshot_signal.emit()

    def minimize(self):
        """Minimize the main window"""
        self.minimize_signal.emit()

    def clear_chat(self):
        """Clear the chat history"""
        self.clear_chat_signal.emit()

    def generate_with_screenshot(self):
        """Automatically generate content with screenshot"""
        self.generate_content_with_screenshot_signal.emit(
"""Help me solve this programming problem. Be concise.
1. Give me 5 clarification questions to ask about the problem.
2. State the type of problem (ex. Arrays & Hashing, Two Pointers, Sliding Window, Stack, Binary Search, Linked List, Trees, Heap / Priority Queue, Backtracking, Tries, Graphs, Advanced Graphs, 1-D Dynamic Programming, 2-D Dynamic Programming, Greedy, Intervals, Math & Geometry, and/or Bit Manipulation), data structure(s), what each element in the data structure means, and algorithm(s) used to solve this problem.
3. Give me a high-level, point-form plan to approach and solve this problem (including edge cases).
4. Give me a short example walkthrough using your solution.
5. Give me a code block with the solution in Python, supplied with comments.
6. Give me a concise explanation of the solution.
7. Give me the time and space complexity for the solution.""",
            True  # Take a screenshot
        )

    def generate_with_screenshot_fix(self):
        """Automatically generate content with screenshot for fixing/improving code"""
        self.generate_content_with_screenshot_signal.emit(
            "Fix or improve the code based on the new instructions. Then, state the changes you made.",
            True  # Take a screenshot
        )
