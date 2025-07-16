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
import os
from playwright.sync_api import sync_playwright
from features import config
from helpers.logger import Logger
from helpers.screenshot_recorder import ScreenshotRecorder

def before_all(context):
    # Logger setup
    context.logger = Logger()
    context.screenshot_recorder = ScreenshotRecorder()

    # Playwright engine start
    context.playwright = sync_playwright().start()

    # Configuration values
    browser_type = getattr(config, "BROWSER_TYPE", "chromium")
    headless = getattr(config, "HEADLESS", True)
    video_dir = getattr(config, "VIDEO_DIR", "recordings/videos")
    screenshot_dir = getattr(config, "SCREENSHOT_DIR", "recordings/screenshots")
    window_size = getattr(config, "WINDOW_SIZE", None)
    video_recording = getattr(config, "VIDEO_RECORDING", False)
    base_url = getattr(config, "BASE_URL", "https://www.playwright.dev/")

    # Directory context for screenshots and videos
    context.video_dir = video_dir

    # Viewport calculation from window_size string
    viewport = None
    if window_size and isinstance(window_size, str) and "x" in window_size:
        width, height = map(int, window_size.split("x"))
        viewport = {"width": width, "height": height}

    # Browser launch arguments (Docker vs Local)
    if os.getenv('RUNNING_IN_DOCKER'):
        browser_args = getattr(config, 'DOCKER_BROWSER_OPTIONS', [])
    else:
        browser_args = getattr(config, 'LOCAL_BROWSER_OPTIONS', [])

    # Browser and context creation
    browser = getattr(context.playwright, browser_type)
    context.browser = browser.launch(headless=headless, args=browser_args)
    context.context = context.browser.new_context(
        record_video_dir=video_dir if video_recording else None,
        viewport=viewport
    )

    # Page creation and navigation to base URL
    context.page = context.context.new_page()
    context.page.goto(base_url)

def after_all(context):
    # Releasing resources
    if hasattr(context, "context"):
        context.context.close()
    if hasattr(context, "browser"):
        context.browser.close()
    if hasattr(context, "playwright"):
        context.playwright.stop()
    if hasattr(context, "logger"):
        context.logger.log_end()

def before_feature(context, feature):
    # Log the start of a feature
    message = f"START  -  FEATURE - {feature.name}"
    context.logger.logger.info(message)
    context.logger.log_to_console(message, 'in_progress')

    # Delete all cookies and session storage
    context.page.context.clear_cookies()
    context.page.evaluate("window.sessionStorage.clear(); window.localStorage.clear();")

def after_feature(context, feature):
    # Log the end of a feature with its status
    status = 'PASSED' if feature.status == 'passed' else 'FAILED'
    message = f"{status} -  FEATURE - {feature.name}"
    context.logger.logger.info(message)
    context.logger.log_to_console(message, feature.status)
    context.logger.logger.info("")

def before_scenario(context, scenario):
    # Log the start of a scenario
    message = f"START  - SCENARIO - {scenario.name}"
    context.logger.logger.info(message)
    context.logger.log_to_console(message, 'in_progress')

    # Delete all cookies and session storage
    if "isolate" in scenario.tags:
        context.page.context.clear_cookies()
        context.page.evaluate("window.sessionStorage.clear(); window.localStorage.clear();")

def after_scenario(context, scenario):
    # Log the end of a scenario with its status
    status = 'PASSED' if scenario.status == 'passed' else 'FAILED'
    message = f"{status} - SCENARIO - {scenario.name}"
    context.logger.logger.info(message)
    context.logger.log_to_console(message, scenario.status)

    # Delete all cookies and session storage
    if "isolate" in scenario.tags:
        context.page.context.clear_cookies()
        context.page.evaluate("window.sessionStorage.clear(); window.localStorage.clear();")

def after_step(context, step):
    # Log the status of a step
    status = 'PASSED' if step.status == 'passed' else 'FAILED'
    message = f"{status} -   STEP   - {step.keyword} {step.name}"
    context.logger.logger.info(message)
    context.logger.log_to_console(message, step.status)

    # Take a screenshot if the step failed
    if step.status == 'failed':
        context.screenshot_recorder.take_screenshot(context)
