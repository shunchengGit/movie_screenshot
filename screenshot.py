# -*- coding: utf-8 -*

from os import listdir
from PIL import Image
from math import ceil
import commands
import re
import sys
import os


def get_time_len(time_len):
	min = 0
	strs = time_len.split(":")
	if cmp(strs[0], "0") > 0:
		min = min + float(strs[0]) * 60 * 60
	if cmp(strs[1], "0") > 0:
		min = min + float(strs[1]) * 60
	if cmp(strs[2], "0") > 0:
		min = min + float(strs[2])
	return float(min)

def get_vedio_info(vedio_path):
	cmd_string = "ffmpeg -i " + FileHelper.cmd_line_path(vedio_path)
	print cmd_string
	output = commands.getstatusoutput(cmd_string)
	return str(output)

def get_vedio_duration(vedio_info):
	if not isinstance(vedio_info, basestring):
		return 0

	if len(vedio_info) == 0:
		return 0
	
	duration = 0
	regex_duration = r"Duration: (.*?), start"
	search_obj = re.search(regex_duration, vedio_info)
	if search_obj:
		duration = get_time_len(search_obj.group(1))
	else:
		print "Not found duration!!!"

	return duration

def get_resolution_ratio(vedio_info):
	regex_duration = r", ([\d]*?)x([\d]*?)\ (.*),\ ([\d]*?)\ kb/s,\ ([\d]*?)\ fps"
	search_obj = re.search(regex_duration, vedio_info)
	if search_obj:
		w = search_obj.group(1)
		h = search_obj.group(2)
		if len(w) > 0:
			w = int(w)
		else:
			w = -1
		if len(h) > 0:
			h = int(h)
		else:
			h = -1
		return w, h
	else:
		print "Not found ratio!!!"
	
	return -1, -1

def get_freq(duration, pic_cnt):
	if duration < 0.00001:
		return 0
	return pic_cnt / duration

def screen_shotcut(freq, start_time, w, h, vedio_path):
	path_helper = FileHelper(vedio_path)
	param_tmp_pic = " " + FileHelper.cmd_line_path(path_helper.tmp_pic_cmd_path())

	param_ratio = ""
	if w > 0 and h > 0:
		param_ratio = " -s " + str(w) + "x" + str(h)

	param_start_time = " -ss " + str(start_time)
	param_vedio_path = " -i " + FileHelper.cmd_line_path(vedio_path)
	param_freq = " -r " + str(freq)
	cmd_string = "ffmpeg" + param_start_time + param_vedio_path + param_freq + " -f image2" + param_ratio + param_tmp_pic
	print cmd_string

	status, output = commands.getstatusoutput(cmd_string)


def save_result_pic(cols, vedio_path):
	path_helper = FileHelper(vedio_path)
	dir_path = path_helper.dir_name
	print dir_path
	print os.path.exists(dir_path)

	file_list = [f for f in listdir(dir_path) if path_helper.is_tmp_pic(f)]
	file_list.sort()
	imglist = [Image.open(path_helper.tmp_pic_path(f)) for f in file_list]

	if cols < 1:
		cols = 1

	rows = int(ceil(len(imglist)/cols))
	if rows < 1:
		rows = 1

	w, h = imglist[0].size

	result = Image.new(imglist[0].mode, (w * cols, h * rows))

	for r in range(rows):
		for c in range(cols):
			i = r * cols + c
			if (i < len(imglist)):
				result.paste(imglist[i], box= (c*w,r*h))

	result.save(path_helper.result_file_path())


def remove_tmp_pics(vedio_path):
	path_helper = FileHelper(vedio_path)
	dir_path = path_helper.dir_name
	print dir_path
	file_list = [f for f in listdir(dir_path) if path_helper.is_tmp_pic(f)]
	for f in file_list:
		filepath = path_helper.tmp_pic_path(f)
		if (os.path.exists(filepath)):
			os.remove(filepath)


class FileHelper:
	"""docstring for FileHelper"""
	def __init__(self, file_path):
		self.file_path = file_path
		self.analyze()

	def analyze(self):
		self.dir_name = os.path.dirname(self.file_path)
		self.file_name = os.path.basename(self.file_path)

		index = self.file_name.rfind('.') 
		if index != -1 :
			self.main_file_name = self.file_name[0:index]
			self.ext_file_name = self.file_name[index:len(self.file_name)]

	def version(self):
		return "_v_0.1"

	def tmp_pic_file_prefix(self):
		return "screen_shotcut_"

	def tmp_pic_cmd_path(self):
		return os.path.join(self.dir_name, self.tmp_pic_file_prefix() + "%3d.jpg")

	def tmp_pic_path(self, file_name):
		return os.path.join(self.dir_name, file_name)

	def is_tmp_pic(self, file_name):
		return file_name.startswith(self.tmp_pic_file_prefix()) and file_name.endswith(".jpg")

	def result_file_path(self):
		return os.path.join(self.dir_name, self.main_file_name + self.version() + "_result.png")

	@staticmethod
	def cmd_line_path(str):
		return str.replace(r" ", r"\ ").replace(r"(", r"\(").replace(r")", r"\)")

	@staticmethod
	def is_movie(file_name):
		ext_name_list = ["rmvb", "mkv", "mp4", "wmv", "avi"];
		for ext in ext_name_list:
			if file_name.lower().endswith(ext):
				return 1

		return 0



def process_vedio(vedio_path):
	cols = 5
	rows = 4
	print vedio_path

	info = get_vedio_info(vedio_path)
	print "############ get_vedio_info"

	duration = get_vedio_duration(info)
	print "############ get_vedio_duration : " + str(duration)

	if duration < 10:
		return;

	freq = get_freq(duration, cols * rows)
	print "############ get_freq : " + str(freq)

	w, h = get_resolution_ratio(info)
	if w > 1024:
		k = 1024.0 / w
		w = int(w * k)
		h = int(h * k)
	print "############ get_resolution_ratio : " + str(w) + "x" + str(h)
	

	start_time = duration * 0.1
	screen_shotcut(freq, str(start_time), w, h, vedio_path)
	print "############ screen_shotcut"

	save_result_pic(cols, vedio_path)
	print "############ save_result_pic"

	remove_tmp_pics(vedio_path)
	print "############ remove_tmp_pics"

def process_dir(dir_name):
	print dir_name
	names = listdir(dir_name)
	for n in names:
		path = os.path.join(dir_name, n)
		if os.path.isdir(path):
			process_dir(path)
		elif os.path.isfile(path):
			if (FileHelper.is_movie(path)):
				process_vedio(path)

def all_file_ext_name(dir_name, s):
	names = listdir(dir_name)
	for p in names:
		path = os.path.join(dir_name, p)
		if os.path.isdir(path):
			all_file_ext_name(path, s)
		elif os.path.isfile(path):
			s.add(os.path.splitext(path)[1])
		else:
			print "N??"

def print_all_file_ext_name(dir_name):
	s = set()
	all_file_ext_name(dir_name, s)
	for e in s:
		print e

print '参数个数为:', len(sys.argv), '个参数。'
print '参数列表:', str(sys.argv)

if len(sys.argv) <= 1:
	print "请输入文件夹"

dir_name = sys.argv[1];

process_dir(dir_name)

# process_vedio(v3)
# print_all_file_ext_name(r"/Volumes/ADATA HV620/")





