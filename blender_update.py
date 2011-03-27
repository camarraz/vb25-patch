__author__ = "Andrey M. Izrantsev http://cgdo.ru"
__version__ = "1.1"

import sys
import os
import shutil
import socket
import platform
import getpass
import re
import string
import glob
import subprocess
import tempfile

from optparse import OptionParser

USER= getpass.getuser()
PLATFORM= sys.platform
HOSTNAME= socket.gethostname()
ARCH= platform.architecture()[0]
REV= 'current'
VERSION= '2.56'

'''
  COMMAND LINE OPTIONS
'''
parser= OptionParser(usage="python %prog [options]", version="blender_update %s by %s" % (__version__, __author__))

parser.add_option(
	'-b',
	'--blender',
	action= 'store_true',
	dest= 'pure_blender',
	default= False,
	help= 'Build Blender 2.5 SVN (don\'t apply V-Ray/Blender patches).'
)

parser.add_option(
	'-a',
	'--archive',
	action= 'store_true',
	dest= 'archive',
	default= False,
	help= 'Create archive (Linux) or installer (Windows, NSIS required).'
)

parser.add_option(
	'-r',
	'--rebuild',
	action= 'store_true',
	dest= 'rebuild',
	default= False,
	help= 'Full rebuild.'
)

parser.add_option(
	'',
	'--docs',
	action= 'store_true',
	dest= 'docs',
	default= False,
	help= 'Build Python API documentation (python-sphinx required).'
)

parser.add_option(
	'',
	'--collada',
	action= 'store_true',
	dest= 'with_collada',
	default= False,
	help= 'Add Collada support.'
)

parser.add_option(
	'',
	'--desktop',
	action= 'store_true',
	dest= 'desktop',
	default= False,
	help= 'Generate desktop file.'
)

parser.add_option(
	'',
	'--blend_files',
	action= 'store_true',
	dest= 'blend_files',
	default= False,
	help= 'Add custom default blend files.'
)

parser.add_option(
	'',
	'--extern',
	action= 'store_true',
	dest= 'extern',
	default= False,
	help= 'Apply \"extern\" patches.'
)

parser.add_option(
	'-d',
	'--debug',
	action= 'store_true',
	dest= 'debug',
	default= False,
	help= 'Debug build.'
)

parser.add_option(
	'-j',
	'--jobs',
	action= 'store_true',
	dest= 'jobs',
	default= 4,
	help= 'Number of build jobs.'
)

parser.add_option(
	'-o',
	'--optimize',
	action= 'store_true',
	dest= 'optimize',
	default= False,
	help= 'Use compiler optimizations.'
)

parser.add_option(
	'-u',
	'--update_blender',
	action= 'store_true',
	dest= 'update',
	default= False,
	help= 'Update sources.'
)

parser.add_option(
	'',
	'--update_patch',
	action= 'store_true',
	dest= 'update_patch',
	default= False,
	help= 'Update patch sources.'
)

parser.add_option(
	'-t',
	'--test',
	action= 'store_true',
	dest= 'test',
	default= False,
	help= 'Test mode.'
)

parser.add_option(
	'',
	'--deps',
	action= 'store_true',
	dest= 'deps',
	default= False,
	help= 'Install dependencies.'
)

parser.add_option(
	'',
	'--devel',
	action= 'store_true',
	dest= 'devel',
	default= False,
	help= 'Developer mode.'
)

if PLATFORM == "win32":
	parser.add_option(
		'',
		'--releasedir',
		dest= 'releasedir',
		help= "Directory for installer and archive."
	)

	parser.add_option(
		'',
		'--installdir',
		dest= 'installdir',
		help= "Installation directory."
	)
else:
	parser.add_option(
		'',
		'--releasedir',
		metavar="FILE",
		dest= 'releasedir',
		help= "Directory for installer and archive."
	)

	parser.add_option(
		'',
		'--installdir',
		metavar="FILE",
		dest= 'installdir',
		help= "Installation directory."
	)

(options, args) = parser.parse_args()

LINUX= platform.linux_distribution()[0].lower().strip()
LINUX_VER= platform.linux_distribution()[1].replace('.','_').strip()

def my_path_join(*args):
	path= None
	if PLATFORM == "win32":
		path= '\\\\'.join(args)
		path= path.replace('\\\\\\\\','\\\\')
	else:
		path= os.path.join(*args)
	return path

DEFAULT_INSTALLPATH= my_path_join(os.getcwd(),"install")
DEFAULT_RELEASEDIR=  my_path_join(os.getcwd(),"release")

if PLATFORM == "win32":
	DEFAULT_INSTALLPATH= my_path_join("C:","vb25","install")
	DEFAULT_RELEASEDIR=  my_path_join("C:","vb25","release")


'''
  PATHS
'''
def get_full_path(path):
	if(path[0:1] == '~'):
		path= my_path_join(os.environ["HOME"],path[2:])
	elif(path[0:1] != '/'):
		path= os.path.abspath(path)
	return path

project= 'vb25'
if options.pure_blender:
	project= 'blender-2.5'

install_dir= DEFAULT_INSTALLPATH
if options.installdir:
	install_dir= get_full_path(options.installdir)
install_dir= my_path_join(install_dir,project)
sys.stdout.write("Installation directory: %s\n" % install_dir)

if not os.path.exists(install_dir):
	sys.stdout.write("Installation directory doesn\'t exist! Trying to create...\n")
	if not options.test:
		os.makedirs(install_dir)

release_dir= DEFAULT_RELEASEDIR
if options.releasedir:
	release_dir= get_full_path(options.releasedir)
sys.stdout.write("Release directory: %s\n" % release_dir)


'''
  MAIN SECTION
'''
def which(program):
	def is_exe(fpath):
		return os.path.exists(fpath) and os.access(fpath, os.X_OK)

	fpath, fname = os.path.split(program)
	if fpath:
		if is_exe(program):
			return program
	else:
		for path in os.environ["PATH"].split(os.pathsep):
			exe_file = my_path_join(path, program)
			if is_exe(exe_file):
				return exe_file

	return None

if PLATFORM == "linux2":
	if options.deps:
		sys.stdout.write("Installing dependencies: ")
		if LINUX == 'ubuntu':
			packages= "subversion build-essential gettext libxi-dev libsndfile1-dev libpng12-dev libfftw3-dev libopenexr-dev libopenjpeg-dev libopenal-dev libalut-dev libvorbis-dev libglu1-mesa-dev libsdl-dev libfreetype6-dev libtiff4-dev libsamplerate0-dev libavdevice-dev libavformat-dev libavutil-dev libavcodec-dev libjack-dev libswscale-dev libx264-dev libmp3lame-dev python3.1-dev git-core libnotify-bin"
			if options.docs:
				packages+= " python-sphinx"
			sys.stdout.write("%s\n" % packages)
			os.system("sudo apt-get install %s" % packages)
		elif LINUX == 'opensuse':
			packages="scons gcc-c++ xorg-x11-devel Mesa-devel xorg-x11-libs zlib-devel libpng-devel xorg-x11 libjpeg-devel freetype2-devel libtiff-devel OpenEXR-devel SDL-devel openal-devel fftw3-devel libsamplerate-devel libjack-devel python3-devel libogg-devel libvorbis-devel freealut-devel update-desktop-files libtheora-devel subversion git-core gettext-tools"
			sys.stdout.write("%s\n" % packages)
			os.system("sudo zypper install %s" % packages)
		elif LINUX == 'redhat' or LINUX == 'fedora':
			packages="gcc-c++ subversion libpng-devel libjpeg-devel libXi-devel openexr-devel openal-soft-devel freealut-devel SDL-devel fftw-devel libtiff-devel lame-libs libsamplerate-devel freetype-devel jack-audio-connection-kit-devel ffmpeg-libs ffmpeg-devel xvidcore-devel libogg-devel faac-devel faad2-devel x264-devel libvorbis-devel libtheora-devel lame-devel python3 python3-devel python3-libs git-core"
			sys.stdout.write("%s\n" % packages)
			os.system("sudo yum install %s" % packages)
		else:
			sys.stdout.write("Your distribution doesn\'t support automatic dependencies installation.\n")
		sys.exit()

working_directory= os.getcwd()

BF_NUMJOBS= options.jobs
if not HOSTNAME.find('vbox') == -1:
	BF_NUMJOBS= 1

BF_PYTHON_VERSION= '3.2'

patch_cmd= 'patch.exe'
if PLATFORM == "win32":
	path= os.getenv('PATH')
	path_list= path.split(';')
	for path in path_list:
		if path.find('Git') != -1:
			if path.find('cmd') != -1:
				patch_cmd= my_path_join(os.path.normpath(my_path_join(path,'..','bin')),'patch.exe')
				sys.stdout.write("Using patch from Git (%s)\n" % patch_cmd)
				break

def notify(title, message):
	if not PLATFORM == "win32":
		if which("notify-send") is not None:
			os.system("notify-send \"%s\" \"%s\"" % (title, message))

def generate_desktop(filepath):
	ofile= open(filepath, 'w')
	ofile.write("[Desktop Entry]\n")
	if project == 'vb25':
		ofile.write("Name=V-Ray/Blender 2.5\n")
	else:
		ofile.write("Name=Blender 2.5\n")
	ofile.write("Exec=%s/blender\n" % install_dir)
	ofile.write("Icon=%s/icons/scalable/blender.svg\n" % install_dir)
	ofile.write("Terminal=true\n")
	ofile.write("Type=Application\n")
	ofile.write("Categories=Graphics;3DGraphics;\n")
	ofile.write("StartupNotify=false\n")
	ofile.write("MimeType=application/x-blender;\n")
	ofile.close()

def generate_installer(patch_dir, BF_INSTALLDIR, INSTALLER_NAME, VERSION):
	DIR= os.getcwd()
	SKIP_DIRS= ('plugins')

	#
	# NSIS installer sciprt template;
	# based on official script by jesterKing
	#

	ns = open(my_path_join(patch_dir,'installer','template.nsi'),"r")
	ns_cnt = str(ns.read())
	ns.close()
	
	ns_cnt = string.replace(ns_cnt, "[PYTHON_VERSION]", BF_PYTHON_VERSION)

	# do root
	rootlist = []
	rootdir = os.listdir(BF_INSTALLDIR+"\\")
	for rootitem in rootdir:
		if os.path.isdir(BF_INSTALLDIR+"\\"+ rootitem) == 0:
			rootlist.append("File \"" + os.path.normpath(BF_INSTALLDIR) + "\\" + rootitem+"\"")
	rootstring = string.join(rootlist, "\n  ")
	rootstring += "\n\n"

	dot_blender_add= ""
	dot_blender_del= ""
	scripts_dirs= []
	for root, dirs, files in os.walk(my_path_join(BF_INSTALLDIR)):
		root_path= string.replace(root, BF_INSTALLDIR, "")
		dot_blender_add+= "\n  SetOutPath \"$BLENDERHOME%s\"\n"%(root_path)
		scripts_dirs.append(root_path)
		for f in os.listdir(root):
			f_path= my_path_join(root,f)
			if os.path.isdir(f_path) == 0:
				dot_blender_del+= "  Delete \"$INSTDIR%s%s\"\n"%(root_path,f)
				dot_blender_add+= "  File \"%s\"\n"%(f_path)

	rootstring+= dot_blender_add
	ns_cnt = string.replace(ns_cnt, "[ROOTDIRCONTS]", rootstring)
	# ns_cnt= string.replace(ns_cnt, "[DOTBLENDER]", dot_blender_add)
	ns_cnt= string.replace(ns_cnt, "[DOTBLENDER]", "")

	# do delete items
	scripts_dirs.reverse()
	for sdir in scripts_dirs:
		dot_blender_del+= '  RMDir /r \"$INSTDIR%s\"\n'%(sdir)

	delrootlist = []
	for rootitem in rootdir:
		if os.path.isdir(BF_INSTALLDIR + rootitem) == 0:
			delrootlist.append("Delete \"$INSTDIR\\%s\\\"" % rootitem)
	delrootstring = string.join(delrootlist, "\n  ")
	delrootstring+= "\n\n"

	ns_cnt = string.replace(ns_cnt, "[DELROOTDIRCONTS]", delrootstring)
	ns_cnt = string.replace(ns_cnt, "[DOTBLENDER_DELETE]", dot_blender_del)
	ns_cnt = string.replace(ns_cnt, "DISTDIR",  BF_INSTALLDIR)
	ns_cnt = string.replace(ns_cnt, "SHORTVER", VERSION)
	ns_cnt = string.replace(ns_cnt, "VERSION",  VERSION)
	ns_cnt = string.replace(ns_cnt, "RELDIR",   my_path_join(patch_dir,'installer'))
	ns_cnt = string.replace(ns_cnt, "[INSTALLER_DIR]", release_dir)
	ns_cnt = string.replace(ns_cnt, "[INSTALLER_NAME]", INSTALLER_NAME)

	inst_nsis= my_path_join(working_directory,"installer.nsi")
	new_nsis = open(inst_nsis, 'w')
	new_nsis.write(ns_cnt)
	new_nsis.close()

	if not options.test:
		os.system("makensis \"%s\""%(inst_nsis))


def generate_user_config(filename):
	ofile= open(filename, 'w')
	ofile.write("# This file is automatically generated: DON\'T EDIT!\n")

	if PLATFORM == "win32":
		build_options= {
			'True': [
				'WITH_BF_FFMPEG',
				'WITH_BF_OPENAL',
				'WITH_BF_SDL',
				'WITH_BF_BULLET',
				'WITH_BF_ZLIB',
				'WITH_BF_FTGL',
				'WITH_BF_RAYOPTIMIZATION',
				'WITH_BUILDINFO',
				'WITH_BF_OPENEXR'
				'WITH_BF_ICONV'
			],
			'False': [
				'WITH_BF_QUICKTIME',
				'WITH_BF_FMOD',
				'WITH_BF_VERSE',
				'WITH_BF_GAMEENGINE',
				'WITH_BF_PLAYER',
				'WITH_BF_JACK',
				'WITH_BF_FFTW3'
			]
		}
	else:
		build_options= {
			'True': [
				'WITH_BF_INTERNATIONAL',
				'WITH_BF_JPEG',
				'WITH_BF_PNG',
				'WITH_BF_OPENAL',
				'WITH_BF_SDL',
				'WITH_BF_BULLET',
				'WITH_BF_ZLIB',
				'WITH_BF_FTGL',
				'WITH_BF_RAYOPTIMIZATION',
				'WITH_BUILDINFO',
				'WITH_BF_OPENEXR'
			],
			'False': [
				'WITH_BF_QUICKTIME',
				'WITH_BF_FMOD',
				'WITH_BF_ICONV',
				'WITH_BF_STATICOPENGL',
				'WITH_BF_VERSE',
				'WITH_BF_GAMEENGINE',
				'WITH_BF_PLAYER'
			]
		}

		if LINUX == 'opensuse':
			build_options['False'].append('WITH_BF_FFMPEG')
			build_options['True'].append('WITHOUT_BF_PYTHON_INSTALL')
		else:
			build_options['True'].append('WITH_BF_FFMPEG')

	# Check this option for Linux:
	#   'WITH_BF_FHS'
	#   Use the Unix "Filesystem Hierarchy Standard" rather then a redistributable directory layout

	if PLATFORM == "win32" and ARCH == '64bit':
		build_options['False'].append('WITH_BF_JACK')
		build_options['False'].append('WITH_BF_SNDFILE')
		build_options['False'].append('WITH_BF_FFMPEG')
		build_options['False'].append('WITH_BF_OPENAL')

	if options.with_collada:
		build_options['True'].append('WITH_BF_COLLADA')
	else:
		build_options['False'].append('WITH_BF_COLLADA')

	if options.debug:
		build_options['True'].append('BF_DEBUG')

	for key in build_options:
		for opt in build_options[key]:
			ofile.write("%s = '%s'\n"%(opt,key))

	ofile.write("BF_PYTHON_VERSION = '%s'\n" % BF_PYTHON_VERSION)

	if PLATFORM == "linux2":
		SUFFIX= ""
		for s in ('m', 'mu', 'd', 'dmu'):
			if os.path.exists("/usr/include/python3.2"+s):
				SUFFIX= s
				break
		ofile.write("SUFFIX = '%s'\n" % SUFFIX)
		LIB = "lib"
		if LINUX == 'opensuse' and ARCH == '64bit':
			LIB = "lib64"
		ofile.write("BF_PYTHON =         '/usr'\n")
		ofile.write("BF_PYTHON_LIBPATH = '${BF_PYTHON}/%s'\n" % LIB)
		ofile.write("BF_PYTHON_INC =     '${BF_PYTHON}/include/python${BF_PYTHON_VERSION}' + SUFFIX\n")
		ofile.write("BF_PYTHON_BINARY =  '${BF_PYTHON}/bin/python${BF_PYTHON_VERSION}'\n")
		ofile.write("BF_PYTHON_LIB =     'python${BF_PYTHON_VERSION}' + SUFFIX\n")

	if not PLATFORM == "win32":
		ofile.write("BF_OPENAL_LIB = \'openal alut\'\n")
	
	ofile.write("BF_TWEAK_MODE = \'false\'\n")
	ofile.write("BF_NUMJOBS = %i\n" % BF_NUMJOBS)

	ofile.write("BF_INSTALLDIR = \"%s\"\n" % install_dir)
	if PLATFORM == "win32" :
		ofile.write("BF_SPLIT_SRC = \'true\'\n")
		ofile.write("BF_BUILDDIR = \"C:\\\\b\"\n")
	else:
		ofile.write("BF_BUILDDIR = \"/tmp/build-%s\"\n" % project)
		if options.optimize: # Optimize for Intel Core
			ofile.write("CCFLAGS = [\'-pipe\',\'-fPIC\',\'-march=nocona\',\'-msse3\',\'-mmmx\',\'-mfpmath=sse\',\'-funsigned-char\',\'-fno-strict-aliasing\',\'-ftracer\',\'-fomit-frame-pointer\',\'-finline-functions\',\'-ffast-math\']\n")
			ofile.write("CXXFLAGS = CCFLAGS\n")
			ofile.write("REL_CFLAGS = [\'-O3\',\'-fomit-frame-pointer\',\'-funroll-loops\']\n")
			ofile.write("REL_CCFLAGS = REL_CFLAGS\n")
		else:
			ofile.write("CCFLAGS = [\'-pipe\',\'-fPIC\',\'-funsigned-char\',\'-fno-strict-aliasing\']\n")
			ofile.write("CPPFLAGS = [\'-DXP_UNIX\']\n")
			ofile.write("CXXFLAGS = [\'-pipe\',\'-fPIC\',\'-funsigned-char\',\'-fno-strict-aliasing\']\n")
			ofile.write("REL_CFLAGS = [\'-O2\']\n")
			ofile.write("REL_CCFLAGS = [\'-O2\']\n")

		ofile.write("C_WARN = [\'-Wno-char-subscripts\', \'-Wdeclaration-after-statement\']\n")
		ofile.write("CC_WARN = [\'-Wall\']\n")

	ofile.close()

notify("%s SVN update" % project, "Started...")

os.chdir(working_directory)

# Update or obtain Blender SVN
blender_dir= my_path_join(working_directory,'blender')
blender_svn_dir= my_path_join(working_directory,'blender-svn')
if os.path.exists(blender_svn_dir):
	os.chdir(blender_svn_dir)
	if options.update:
		sys.stdout.write("Updating Blender sources...\n")
		if not options.test:
			os.system("svn update")
			os.chdir(working_directory)
			if PLATFORM == "win32":
				os.system("rmdir /Q /S %s" % blender_dir)
			else:
				os.system("rm -rf %s" % blender_dir)
			os.system("svn export blender-svn blender")

	try:
		entries= open(my_path_join(blender_svn_dir,'.svn','entries'), 'r').read()
	except IOError:
		pass
	else:
		if re.match('(\d+)', entries):
			rev_match= re.search('\d+\s+dir\s+(\d+)', entries)
			if rev_match:
				REV= rev_match.groups()[0]

else:
	sys.stdout.write("Getting Blender sources...\n")
	if not options.test:
		os.system("svn checkout https://svn.blender.org/svnroot/bf-blender/trunk/blender")
		os.system("mv blender blender-svn")
		os.system("svn export blender-svn blender")

#version_file= open(my_path_join(blender_svn_dir,"release","VERSION"),'r')
#VERSION= version_file.read().split('-')[0]
#version_file.close()

os.chdir(working_directory)

# Update 'lib' on Windows
if PLATFORM == "win32":
	lib_dir= my_path_join(working_directory,'lib','windows')
	# if ARCH == '64bit':
	# 	lib_dir= my_path_join(working_directory,'lib','win64')
	if os.path.exists(lib_dir):
		os.chdir(lib_dir)
		if options.update:
			sys.stdout.write("Updating lib sources\n")
			if not options.test:
				os.system("svn update")
	else:
		# if ARCH == '64bit':
		# 	os.system("svn checkout https://svn.blender.org/svnroot/bf-blender/trunk/lib/win64 lib/win64")
		# else:
		sys.stdout.write("Getting lib sources\n")
		if not options.test:
			os.system("svn checkout https://svn.blender.org/svnroot/bf-blender/trunk/lib/windows lib/windows")

os.chdir(working_directory)

# Apply V-Ray/Blender patches if needed
def run_patch(patch_file):
	if PLATFORM == "win32":
		cmd= "\"%s\" -Np0 -i %s" % (patch_cmd, patch_file)
	else:
		cmd= "patch -Np0 -i %s" % (patch_file)

	if not options.test:
		os.system(cmd)
	else:
		print cmd
	
patch_dir= my_path_join(working_directory,'vb25-patch')
if not options.pure_blender:
	if os.path.exists(patch_dir):
		os.chdir(patch_dir)
		if options.update_patch:
			sys.stdout.write("Updating vb25 patches\n")
			if not options.test:
				os.system("git pull")
	else:
		sys.stdout.write("Getting vb25 patches\n")
		if not options.test:
			os.system("git clone --depth=1 git://github.com/bdancer/vb25-patch.git")
	os.chdir(working_directory)

	if not options.test:
		shutil.copy(my_path_join(patch_dir, "splash.png.c"), my_path_join(blender_dir,"source","blender","editors","datafiles"))
		dst= my_path_join(blender_dir,"source","blender","exporter")
		if(os.path.exists(dst)):
			shutil.rmtree(dst)
		shutil.copytree(my_path_join(patch_dir, "exporter"), dst)

		os.chdir(blender_dir)
		sys.stdout.write("Applying vb25 patches...\n")
		run_patch(my_path_join(patch_dir,"vb25.patch"))

		if options.extern:
			sys.stdout.write("Applying \"extern\" patches...\n")
			extern_path= my_path_join(patch_dir,"extern")
			for f in os.listdir(extern_path):
				patch_file= my_path_join(extern_path, f)

				run_patch(patch_file)

	if options.blend_files:
		if options.test:
			sys.stdout.write("Replacing startup and preview blend-files...\n")
			editor_datafiles= my_path_join(blender_dir, "source", "blender", "editors", "datafiles")
			datatoc=          my_path_join(blender_dir, "release", "datafiles", "datatoc.py")

			# Doint all in TMP
			os.chdir(tempfile.gettempdir())

			for datafile in ("splash.png", "startup.blend", "preview.blend"):
				datafile_path= my_path_join(patch_dir, datafile)
				cmd= []
				cmd.append(datatoc)
				cmd.append(datafile_path)
				print(' '.join(cmd))
				#shutil.copy(datafile_path+'.c', editor_datafiles)


# Generate user settings file
sys.stdout.write("Generating user-config.py\n")
if not options.test:
	generate_user_config(my_path_join(blender_dir,'user-config.py'))


# Cleaning release dir
if PLATFORM == "win32":
	os.system("rmdir /Q /S %s" % install_dir)


# Finally build Blender
sys.stdout.write("Building %s (%s)\n" % (project,REV))
if not options.test:
	os.chdir(blender_dir)
	build_cmd= "python scons/scons.py"
	if options.rebuild:
		os.system("%s clean" % build_cmd)
	if not options.rebuild:
		build_cmd+= " --implicit-deps-unchanged --max-drift=1"
	os.system(build_cmd)


# Generating .desktop file
if PLATFORM == "linux2" and options.desktop:
	desktop_file= my_path_join(working_directory, "%s.desktop" % project)
	sys.stdout.write("Generating .desktop file: %s\n" % (os.path.basename(desktop_file)))
	if not options.test and not options.devel:
		generate_desktop(desktop_file)
		os.system("sudo mv -f %s /usr/share/applications/" % desktop_file)
	

# Generate docs
if options.docs:
	if PLATFORM == "win32":
		sys.stdout.write("Docs generation on Windows is not supported\n")
	else:
		api_dir= my_path_join(install_dir,'api')
		sys.stdout.write("Generating docs: %s\n" % (api_dir))
		if not options.test:
			sphinx_doc_gen= "doc/python_api/sphinx_doc_gen.py"
			os.system("mkdir -p %s" % api_dir)
			os.chdir(blender_dir)
			os.system("%s -b -P %s" % (my_path_join(install_dir,'blender'), sphinx_doc_gen))
			os.system("sphinx-build doc/python_api/sphinx-in %s" % api_dir)


# Adding exporter
if not options.pure_blender:
	sys.stdout.write("Adding vb25 exporter...\n")
	io_scripts_path= my_path_join(install_dir,VERSION,'scripts','startup')
	exporter_path= my_path_join(io_scripts_path,'vb25')
	if not options.test:
		if os.path.exists(exporter_path):
			if PLATFORM == "win32":
				os.system("rmdir /Q /S %s" % exporter_path)
			else:
				shutil.rmtree(exporter_path)
		if options.devel and not options.archive:
			if not options.test:
				os.symlink(get_full_path('~/devel/vrayblender/exporter/symlinks'), exporter_path)
		else:
			os.chdir(io_scripts_path)
			os.system("git clone --depth=1 git://github.com/bdancer/vb25.git")
os.chdir(working_directory)


# Generate archive (Linux) or installer (Windows)
if not options.debug and options.archive:
	if not os.path.exists(release_dir):
		sys.stdout.write("Release directory doesn\'t exist! Trying to create...\n")
		os.makedirs(release_dir)

	archive_name= "%s-%s-%s%s-%s.tar.bz2" % (project,REV,LINUX,LINUX_VER,ARCH)
	if PLATFORM == "win32":
		archive_name= "%s-%s-win%s.exe" % (project,REV,ARCH[:-3])

	if PLATFORM == "win32":
		sys.stdout.write("Generating installer: %s\n" % (archive_name))
	else:
		sys.stdout.write("Generating archive: %s\n" % (archive_name))

	os.chdir(working_directory)
	if not options.test:
		if PLATFORM == "win32":
			generate_installer(patch_dir, install_dir, archive_name, VERSION)
		else:
			os.chdir(install_dir)
			os.chdir('..')
			os.system("tar jcf %s %s" % (my_path_join(release_dir,archive_name),project))


notify("%s SVN update" % project, "Finished!")

