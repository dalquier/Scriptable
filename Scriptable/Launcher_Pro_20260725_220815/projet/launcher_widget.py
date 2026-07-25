from __future__ import annotations

from urllib.parse import quote
import os
import widgets as wd

ROOT = os.path.dirname(os.path.abspath(__file__))
LAUNCHER = os.path.join(ROOT, "LauncherPro.py")
CODE = f"import runpy; runpy.run_path({LAUNCHER!r}, run_name='__main__')"
URL = "pyto://x-callback/?code=" + quote(CODE, safe="")

widget = wd.Widget()
widget.background_color = wd.Color(0.06, 0.09, 0.16, 1)
stack = wd.VStack()
stack.spacer()
button = wd.Text("↻")
button.font = wd.Font.system_font(42)
button.color = wd.Color(0.95, 0.97, 1.0, 1)
button.link = URL
stack.add(button)
label = wd.Text("Launcher Pro")
label.font = wd.Font.bold_system_font(14)
label.color = wd.Color(0.95, 0.97, 1.0, 1)
label.link = URL
stack.add(label)
stack.spacer()
widget.add(stack)
wd.show_widget(widget)
