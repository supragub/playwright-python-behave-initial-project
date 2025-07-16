"""
playwright-python-behave-initial-project - Behave test framework with Playwright support
Copyright (C) 2025  Gábor Varga

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from playwright.sync_api import sync_playwright

class BrowserInitializer:
    def __init__(self, config):
        self.config = config
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def setup_browser(self, context):
        self.playwright = sync_playwright().start()
        browser_type = getattr(self.playwright, self.config.BROWSER_TYPE)
        headless = getattr(self.config, "HEADLESS", True)
        window_size = getattr(self.config, "WINDOW_SIZE", None)
        viewport = None
        if window_size and isinstance(window_size, str) and "x" in window_size:
            width, height = map(int, window_size.split("x"))
            viewport = {"width": width, "height": height}
        self.browser = browser_type.launch(headless=headless)
        self.context = self.browser.new_context(
            record_video_dir=self.config.VIDEO_DIR if getattr(self.config, "VIDEO_RECORDING", False) else None,
            viewport=viewport
        )
        self.page = self.context.new_page()
        context.page = self.page

    def set_window_size(self, page, size):
        page.set_viewport_size(size)

    def close(self):
        self.context.close()
        self.browser.close()
        self.playwright.stop()
