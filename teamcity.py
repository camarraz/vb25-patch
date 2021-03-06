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

    sys.stdout.write('temacity args:\n%s\n' % str(args))
    sys.stdout.flush()

    if sys.platform == 'win32':
        # Setup Visual Studio 2013 variables for usage from command line
        # Assumes default installation path
        #
        # PATH
        #
        PATH = os.environ['PATH'].split(';')
        PATH.extend([
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
            r'C:\Program Files (x86)\Windows Kits\8.1\Windows Performance Toolkit',
            r'C:\Program Files\Microsoft SQL Server\110\Tools\Binn',
            r'C:\Program Files (x86)\CMake\bin',
            r'C:\Program Files\SlikSvn\bin',
            r'C:\Program Files\Git\bin',
            r'C:\Program Files (x86)\WinSCP',
        ])

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

    os.environ['http_proxy'] = '10.0.0.1:1234'
    os.environ['https_proxy'] = '10.0.0.1:1234'
    os.environ['ftp_proxy'] = '10.0.0.1:1234'
    os.environ['socks_proxy'] = '10.0.0.1:1080'

    os.environ['http_proxy'] = 'http://10.0.0.1:1234/'
    os.environ['https_proxy'] = 'https://10.0.0.1:1234/'

    cmd = [python_exe]
    cmd.append("vb25-patch/build.py")
    cmd.append("--teamcity")
    cmd.append("--teamcity_project_type=%s" % args.teamcity_project_type)
    cmd.append("--teamcity_branch_hash=%s" % args.teamcity_branch_hash)

    branch = args.teamcity_branch
    if branch == '':
        branch = 'dev/vray_for_blender/%s' % args.teamcity_project_type
        sys.stdout.write('No branch specified - using %s' % branch)
        sys.stdout.flush()

    cmd.append('--github-src-branch=%s' % branch)
    cmd.append('--teamcity_zmq_server_hash=%s' % args.teamcity_zmq_server_hash[:7])

    # Teamcity is cloning the sources for us
    cmd.append('--uppatch=off')
    cmd.append('--upblender=off')

    if args.clean:
        cmd.append('--build_clean')

    cmd.append('--with_ge')
    cmd.append('--with_player')
    cmd.append('--with_collada')
    cmd.append('--vc_2013')
    cmd.append('--build_mode=release')
    cmd.append('--build_type=%s' % args.teamcity_build_type)
    cmd.append('--use_package')
    cmd.append('--use_installer=CGR')
    cmd.append('--dir_cgr_installer=%s' % os.path.join(os.getcwd(), 'blender-for-vray-libs', 'cgr_installer'))

    if args.teamcity_with_static_libc:
        cmd.append('--teamcity_with_static_libc')

    if args.teamcity_with_cycles:
        cmd.append('--with_cycles')

    if args.teamcity_zmq_server_hash != '' and args.teamcity_project_type == 'vb35':
        cmd.append('--github-exp-branch=dev/vb35')

    if sys.platform == 'win32':
        cmd.append('--dir_install=H:/install/vray_for_blender')
        cmd.append('--dir_release=H:/release/vray_for_blender')
    else:
        if sys.platform == 'linux':
            cmd.append('--gcc=gcc-4.9.3')
            cmd.append('--gxx=g++-4.9.3')
            cmd.append('--dir_blender_libs=%s' % '/opt/tc-libs')
            cmd.append('--dev_static_libs')

        cmd.append('--dir_install=%s' % os.path.expanduser("~/install/vray_for_blender"))
        cmd.append('--dir_release=%s' % os.path.expanduser("~/release/vray_for_blender"))

    if args.upload:
        cmd.append('--use_package_upload=ftp')
        cmd.append('--use_proxy=http://10.0.0.1:1234')

    sys.stdout.write('Calling builder:\n%s\n' % '\n\t'.join(cmd))
    sys.stdout.flush()

    return subprocess.call(cmd, cwd=os.getcwd())


if __name__ == '__main__':
    import argparse
    import sys

    parser = argparse.ArgumentParser(usage="python3 build.py [options]")

    parser.add_argument('--upload',
        default=False,
        help="Upload build"
    )

    parser.add_argument('--clean',
        default=False,
        help="Clean build directory"
    )

    parser.add_argument('--teamcity_branch_hash',
        default = ""
    )

    parser.add_argument('--teamcity_branch',
        default = "",
    )

    parser.add_argument('--teamcity_project_type',
        choices=['vb30', 'vb35'],
        default = 'vb30',
    )

    parser.add_argument('--teamcity_zmq_server_hash',
        default = "",
    )

    parser.add_argument('--teamcity_with_cycles',
        action = 'store_true',
    )

    parser.add_argument('--teamcity_build_type',
        choices=['debug', 'release'],
        default = 'release',
    )

    parser.add_argument('--teamcity_with_static_libc',
        action = 'store_true',
    )

    args = parser.parse_args()

    sys.exit(main(args))
