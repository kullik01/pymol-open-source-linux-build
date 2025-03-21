"""
#A* -------------------------------------------------------------------
#B* This file contains source code for running automation tasks related
#-* to the build process of the PyMOL computer program
#C* Copyright 2025 by Martin Urban.
#D* -------------------------------------------------------------------
#E* It is unlawful to modify or remove this copyright notice.
#F* -------------------------------------------------------------------
#G* Please see the accompanying LICENSE file for further information.
#H* -------------------------------------------------------------------
#I* Additional authors of this source file include:
#-*
#-*
#-*
#Z* -------------------------------------------------------------------
"""
import argparse
import pathlib
import subprocess
import shutil
import sys

import toml

pyproject_toml = toml.load("pyproject.toml")
PROJECT_NAME = pyproject_toml["project"]["name"]
PROJECT_VERSION = pyproject_toml["project"]["version"]

PROJECT_ROOT_DIR = pathlib.Path(__file__).parent

PYTHON_EXECUTABLE = sys.executable  # This gives the current Python executable
DEBUG = False


class BuildLinuxExe:
  """Contains the logic for building the Linux EXE file."""

  def __init__(self) -> None:
    """Constructor."""
    self.src_path = pathlib.Path(PROJECT_ROOT_DIR / "pymol")
    self.pymol_data_path = pathlib.Path(PROJECT_ROOT_DIR / "pymol/pymol/data")
    self.build_script_filepath = pathlib.Path(
      PROJECT_ROOT_DIR / "pymol", "build_linux_exe.py"
    )
    self.license_filepath = pathlib.Path(PROJECT_ROOT_DIR / "pymol/LICENSE")
    self.readme_filepath = pathlib.Path(PROJECT_ROOT_DIR / "pymol/README.md")
    self.build_dir = pathlib.Path(PROJECT_ROOT_DIR / "pymol/build")

  def setup_build_environment(self) -> None:
    """Sets up a temporary build environment."""
    # <editor-fold desc="Path/Filepath definitions">
    tmp_build_script_filepath = pathlib.Path(
      PROJECT_ROOT_DIR / "scripts/python", "build_linux_exe.py"
    )
    tmp_vendor_pymol_path = pathlib.Path(
      PROJECT_ROOT_DIR / "vendor/pymol-open-source"
    )
    tmp_pymol_python_src_path = pathlib.Path(
      tmp_vendor_pymol_path / "modules"
    )
    tmp_pymol_data_path = pathlib.Path(
      tmp_vendor_pymol_path / "data"
    )
    tmp_pymol_license_filepath = pathlib.Path(
      tmp_vendor_pymol_path / "LICENSE"
    )
    tmp_pymol_readme_filepath = pathlib.Path(
      tmp_vendor_pymol_path / "README.md"
    )
    tmp_edited_pmg_qt_filepath = pathlib.Path(
      PROJECT_ROOT_DIR / "edited/pmg_qt" / "pymol_qt_gui.py"
    )
    tmp_edited_base_css_filepath = pathlib.Path(
      PROJECT_ROOT_DIR / "edited/pymol/data/pymol", "base.css"
    )
    tmp_edited_init_py_filepath = pathlib.Path(
      PROJECT_ROOT_DIR / "edited/pymol", "__init__.py"
    )
    tmp_alternative_splash_screen_filepath = pathlib.Path(
      PROJECT_ROOT_DIR / "alternative_design" / "splash.png"
    )
    # </editor-fold>
    # <editor-fold desc="Copy operations">
    shutil.copytree(tmp_pymol_python_src_path, self.src_path, dirs_exist_ok=True)
    shutil.copytree(tmp_pymol_data_path, self.pymol_data_path, dirs_exist_ok=True)
    shutil.copy(tmp_build_script_filepath, self.build_script_filepath)
    shutil.copy(tmp_pymol_license_filepath, self.license_filepath)
    shutil.copy(tmp_pymol_readme_filepath, self.readme_filepath)
    # <editor-fold desc="Custom file replacements">
    shutil.copy(
      tmp_edited_base_css_filepath,
      pathlib.Path(tmp_pymol_data_path / "pymol", "base.css")
    )
    shutil.copy(
      tmp_edited_pmg_qt_filepath,
      pathlib.Path(self.src_path / "pmg_qt", "pymol_qt_gui.py")
    )
    shutil.copy(
      tmp_edited_init_py_filepath,
      pathlib.Path(self.src_path / "pymol", "__init__.py")
    )
    shutil.copy(
      tmp_alternative_splash_screen_filepath,
      pathlib.Path(self.src_path / "pymol/data/pymol", "splash.png")
    )
    # </editor-fold>
    # </editor-fold>

  def build(self) -> None:
    """Builds the PyMOL Windows EXE file."""
    self.setup_build_environment()
    subprocess.run(
      [PYTHON_EXECUTABLE, self.build_script_filepath],
      stdout=sys.stdout, stderr=sys.stderr, text=True, cwd=self.src_path
    )
    shutil.copytree(self.build_dir, pathlib.Path(PROJECT_ROOT_DIR / "dist"),
                    dirs_exist_ok=True)
    # <editor-fold desc="Clean up">
    if not DEBUG:
      shutil.rmtree(self.src_path)
    # </editor-fold>


def copy_pymol_sources() -> None:
  """Copies the pymol python sources from the vendor directory."""
  tmp_src_path = pathlib.Path(PROJECT_ROOT_DIR / "src/python")
  tmp_pymol_python_src_path = pathlib.Path(PROJECT_ROOT_DIR / "vendor/pymol-open-source/modules")
  if not tmp_src_path.exists():
    print("Copying the pymol python sources ...")
    tmp_src_path.mkdir(parents=True)
    shutil.copytree(
      tmp_pymol_python_src_path,
      tmp_src_path,
      dirs_exist_ok=True
    )


def setup_dev_env() -> None:
  """Installs the dependencies needed for building the _cmd extension module."""
  # <editor-fold desc="Setup pymol-open-source repository">
  if not pathlib.Path(f"{PROJECT_ROOT_DIR}/vendor/pymol-open-source").exists():
    subprocess.run(["git", "clone", "https://github.com/schrodinger/pymol-open-source.git",
                    pathlib.Path(f"{PROJECT_ROOT_DIR}/vendor/pymol-open-source")])
    subprocess.run(["git", "checkout", "0313aeba9d75f464e4dddccc3bdbee71a5afb049"],
                   cwd=pathlib.Path(f"{PROJECT_ROOT_DIR}/vendor/pymol-open-source"))
    subprocess.run([pathlib.Path(f"{PROJECT_ROOT_DIR}/.venv/bin/python3.11"), pathlib.Path(f"{PROJECT_ROOT_DIR}/scripts/python/create_generated_files.py")])
  else:
    print("pymol-open-source already setup.")
  # </editor-fold>
  if not pathlib.Path(f"{PROJECT_ROOT_DIR}/vendor/vcpkg").exists():
    subprocess.run(["git", "clone", "https://github.com/microsoft/vcpkg.git", pathlib.Path(f"{PROJECT_ROOT_DIR}/vendor/vcpkg")])
    subprocess.run(["chmod", "+x", "./bootstrap-vcpkg.sh"], cwd=pathlib.Path(PROJECT_ROOT_DIR / "vendor/vcpkg"))
    subprocess.run(["./bootstrap-vcpkg.sh"], shell=True, cwd=pathlib.Path(PROJECT_ROOT_DIR / "vendor/vcpkg"))
  else:
    print("vcpkg already setup.")


def build_linux_exe() -> None:
  """Builds the Windows EXE file using the BuildWinExe class."""
  tmp_build_linux_exe = BuildLinuxExe()
  tmp_build_linux_exe.build()


def clean_install() -> None:
  """Cleans the CMake build directory and then runs the complete build process."""
  tmp_pip_executable = pathlib.Path(PROJECT_ROOT_DIR / ".venv/bin", "pip")
  tmp_build_dir = pathlib.Path(PROJECT_ROOT_DIR / "cmake-build-setup_py")
  copy_pymol_sources()

  if tmp_build_dir.exists():
    shutil.rmtree(tmp_build_dir)
  subprocess.run(
    [tmp_pip_executable, 'install', '.'],
    stdout=sys.stdout, stderr=sys.stderr, text=True
  )


def build_wheel() -> None:
  """Builds the wheel file for the python PyMOL package."""
  # Run the command using subprocess.run
  copy_pymol_sources()
  _CMD_FROM_BUILD_DIR = pathlib.Path(PROJECT_ROOT_DIR / "cmake-build-release" / "_cmd.cpython-311-x86_64-linux-gnu.so")
  _CMD_FROM_PRE_BUILT_DIR = pathlib.Path(PROJECT_ROOT_DIR / "pre-built" / "_cmd.cpython-311-x86_64-linux-gnu.so")
  if _CMD_FROM_BUILD_DIR.exists():
    shutil.copy(
      _CMD_FROM_BUILD_DIR,
      pathlib.Path(PROJECT_ROOT_DIR / "src/python/pymol" / "_cmd.cpython-311-x86_64-linux-gnu.so")
    )
  else:
    shutil.copy(
      _CMD_FROM_PRE_BUILT_DIR,
      pathlib.Path(PROJECT_ROOT_DIR / "src/python/pymol" / "_cmd.cpython-311-x86_64-linux-gnu.so")
    )
  subprocess.run(
    [PYTHON_EXECUTABLE, 'setup.py', 'sdist', 'bdist_wheel'],
    stdout=sys.stdout, stderr=sys.stderr, text=True
  )
  shutil.rmtree(pathlib.Path(PROJECT_ROOT_DIR / "src"))


def main() -> None:
  """Main function."""
  parser = argparse.ArgumentParser(description="Automation script with subcommands.")
  # <editor-fold desc="Subparsers">
  subparsers = parser.add_subparsers(dest='command')
  install_parser = subparsers.add_parser('setup-dev-env', help="Installs build dependencies.")
  install_parser.set_defaults(func=setup_dev_env)
  build_wheel_parser = subparsers.add_parser('build-wheel', help="Builds the wheel file.")
  build_wheel_parser.set_defaults(func=build_wheel)
  build_linux_exe_parser = subparsers.add_parser('build-linux-exe', help="Builds the GNU Linux EXE file.")
  build_linux_exe_parser.set_defaults(func=build_linux_exe)
  clean_install_parser = subparsers.add_parser('clean-install',
                                               help="Cleans the cmake-build-setup_py diretory and then runs the pip install . command.")
  clean_install_parser.set_defaults(func=clean_install)
  # </editor-fold>
  args = parser.parse_args()

  if args.command:
    args.func()


if __name__ == "__main__":
  main()
