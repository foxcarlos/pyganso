from distutils.core import setup
import py2exe

setup(name="pyGanso",
      version="1.0",
      license="GPL",
    windows=[{"script":"frmcitas.py", "icon_resources":[(1, "img/Ganso.png")]}])

