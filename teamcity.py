#
# V-Ray For Blender TeamCity Build Wrapper
#
# http://chaosgroup.com
#
# Author: Andrei Izrantcev
# E-Mail: andrei.izrantcev@chaosgroup.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# All Rights Reserved. V-Ray(R) is a registered trademark of Chaos Software.
#


def main(args):
    import os
    import sys
    import subprocess

    python_exe = sys.executable

    if sys.platform == 'win32':
        # Setup Visual Studio 2013 variables for usage from command line
        #

        # PATH
        #
        PATH = (
            r'C:\Program Files (x86)\Microsoft Visual Studio 12.0\Common7\IDE\CommonExtensions\Microsoft\TestWindow',
            r'C:\Program Files (x86)\MSBuild\12.0\bin\amd64',
            r'C:\Program Files (x86)\Microsoft Visual Studio 12.0\VC\BIN\amd64',
            r'C:\Windows\Microsoft.NET\Framework64\v4.0.30319',
            r'C:\Program Files (x86)\Microsoft Visual Studio 12.0\VC\VCPackages',
            r'C:\Program Files (x86)\Microsoft Visual Studio 12.0\Common7\IDE',
            r'C:\Program Files (x86)\Microsoft Visual Studio 12.0\Common7\Tools',
            r'C:\Program Files (x86)\HTML Help Workshop',
            r'C:\Program Files (x86)\Microsoft Visual Studio 12.0\Team Tools\Performance Tools\x64',
            r'C:\Program Files (x86)\Microsoft Visual Studio 12.0\Team Tools\Performance Tools',
            r'C:\Program Files (x86)\Windows Kits\8.1\bin\x64',
            r'C:\Program Files (x86)\Windows Kits\8.1\bin\x86',
            r'C:\Program Files (x86)\Microsoft SDKs\Windows\v8.1A\bin\NETFX 4.5.1 Tools\x64',
            r'C:\ProgramData\Oracle\Java\javapath',
            r'C:\Windows\system32',
            r'C:\Windows',
            r'C:\Windows\System32\Wbem',
            r'C:\Windows\System32\WindowsPowerShell\v1.0',
            r'C:\Program Files (x86)\NVIDIA Corporation\PhysX\Common',
            r'C:\Program Files\Git\cmd',
            r'C:\Program Files\SlikSvn\bin',
            r'C:\Program Files (x86)\Windows Kits\8.1\Windows Performance Toolkit',
            r'C:\Program Files\Microsoft SQL Server\110\Tools\Binn',
        )

        INCLUDE = (
            r'C:\Program Files (x86)\Microsoft Visual Studio 12.0\VC\INCLUDE',
            r'C:\Program Files (x86)\Microsoft Visual Studio 12.0\VC\ATLMFC\INCLUDE',
            r'C:\Program Files (x86)\Windows Kits\8.1\include\shared',
            r'C:\Program Files (x86)\Windows Kits\8.1\include\um',
            r'C:\Program Files (x86)\Windows Kits\8.1\include\winrt',
        )

        LIB = (
            r'C:\Program Files (x86)\Microsoft Visual Studio 12.0\VC\LIB\amd64',
            r'C:\ProgramFiles (x86)\Microsoft Visual Studio 12.0\VC\ATLMFC\LIB\amd64',
            r'C:\Program Files (x86)\Windows Kits\8.1\lib\winv6.3\um\x64',
        )

        LIBPATH = (
            r'C:\Windows\Microsoft.NET\Framework64\v4.0.30319',
            r'C:\Program Files (x86)\Microsoft Visual Studio 12.0\VC\LIB\amd64',
            r'C:\Program Files (x86)\Microsoft Visual Studio 12.0\VC\ATLMFC\LIB\amd64',
            r'C:\Program Files (x86)\Windows Kits\8.1\References\CommonConfiguration\Neutral',
            r'C:\Program Files (x86)\Microsoft SDKs\Windows\v8.1\ExtensionSDKs\Microsoft.VCLibs\12.0\References\CommonConfiguration\neutral',
        )

        os.environ['PATH']    = ";".join(PATH)
        os.environ['INCLUDE'] = ";".join(INCLUDE)
        os.environ['LIB']     = ";".join(LIB)
        os.environ['LIBPATH'] = ";".join(LIBPATH)

    cmd = [python_exe]
    cmd.append("vb25-patch/build.py")
    cmd.append("--teamcity")
    cmd.append("--teamcity_branch_hash=\"%s\"" % args.teamcity_branch_hash)

    # Teamcity is cloning the sources for us
    cmd.append("--uppatch=off")
    cmd.append("--upblender=off")

    cmd.append("--release")
    cmd.append("--package")

    if upload:
        cmd.append("--upload=ftp")
        cmd.append("--proxy=10.0.0.1:1234")

    return subprocess.call(cmd, cwd=os.getcwd())


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(usage="python3 build.py [options]")

    parser.add_argument('--upload',
        default=False,
        help="Upload build"
    )

    parser.add_argument('--teamcity_branch_hash',
        default = "",
        help    = argparse.SUPPRESS
    )

    args = parser.parse_args()

    return main(args)