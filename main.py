"""
1. 按需将视频裁剪✔
2. 提取视频图片✔
3. 随机进行删图片 ✔
4. 将图片按顺序 放到一个新的文件夹，注意内存释放 ✔
5. 融合成视频✔
6. 根据视频长添加音频
    超长的删去，不够的补足
"""
import os, shutil,time, random
import sys, traceback
from core.TXT import Txt
from core import pathex, VideoEditor as VE
from pathlib import Path, PurePath




class VideoFuse():
    def __init__(self):
        self.base                  = r"./workspace/"
        self.video_path            = r".\workspace\视频\\"
        self.operator_file         = r".\workspace\操作.txt"
        self.cuted_video_path      = r".\workspace\temp\cut_video"
        self.output_path           = r"./workspace/temp/video_frames/"  # 存放抽取图片的位置
        self.fuse_path             = r"./workspace/temp/fuseSpace/" #存放准融合的图片
        self.output_file           = r".\workspace\融合的视频.mp4"
        self.audio_path            = "./workspace/音频/"

        ####################################################################################################
        #以下是默认值，在 readOperator 里可以更改
        self.algorithm = "1"
        self.al11,self.al12 = 10, 25 #从 算法1： al11 和 al12 中随机抽取 一个数字作为要抽取删掉的百分比 区间是 10-30%
        # self.al21, self.al22 = 10, 25  # 算法二 删除的随机性更大，但数量少
        self.num_del_imgs = 0 #记录删掉多少张图片

    def creat_files(self):
        Path(self.base).mkdir(parents=True, exist_ok=True)
        Path(self.base + "temp").mkdir(parents=True, exist_ok=True)
        Path(self.base + "视频").mkdir(parents=True, exist_ok=True)
        Path(self.base + "音频").mkdir(parents=True, exist_ok=True)
        if not Path(self.base + "操作.txt").is_file():
            txt = ["算法设定:  (共有两个算法，默认算法1， 10-25 是要随机抽帧的比例，建议不要超过50）",
                   "1/10/25","视频名字/开始时间/结束时间  (如果某个视频不想剪辑设置成 0/0 3/0/0)",
                   "1/2s/5s","2/1/3","3/1/2","4/3/6s"]
            Txt(self.base + "操作.txt").writelist(txt)

    def check_path(self, base_name, file_name=None):
        '''base_name 文件夹的基础路径， file_name是想要找的文件
        '''
        path = base_name + f"{file_name}.*"
        path = Path(path)
        path = pathex.get_first_file_by_stem(path.parent, path.stem)
        if path and os.path.isfile(path):
            return path
        else:
            raise FileNotFoundError(f"没有找到名字为:{file_name} 的视频文件")

    def readOperator(self) :
        #读取文档 获取每个视频截取多少
        info = Txt(self.operator_file).readall()
        info_= info[1].split("/")
        self.algorithm, self.al11, self.al12 = info_[0], int(info_[1]), int(info_[2])
        dct = {}
        for i in info[3:]:
            file, start, end = i.split("/")
            if file not in dct:
                start = start.strip().replace("s","")
                end = end.strip().replace("s", "")
                if float(start) >= float(end):
                    raise IndexError("剪辑的开始时间要小于结束时间")
                dct[file] = [start, end]
        return dct

    def trim(self,dct):#剪辑视频
        start = time.time()
        if not os.path.exists(self.cuted_video_path): os.mkdir(self.cuted_video_path)
        for key, value in dct.items():
            video_path = self.check_path(self.video_path, file_name=key)
            video_name = os.path.basename(video_path)
            output_path = os.path.join(self.cuted_video_path, video_name)
            if value[0]  < value[1]: # 如开始时间小于结束时间开始裁剪
                # print(video_path, output_path)
                VE.trim_video(video_path, output_path, value[0], value[1])
            elif int(value[0]) == int(value[1]) == 0: #说明不需要剪辑 直接移动
                shutil.copy(video_path, output_path)
                # print(video_path, output_path)
        self.sum_cut = f"共用时{time.time() - start:.2f}s，剪辑{len(dct)}视频"

    def extract_imgs_from_video(self):
        '''抽取图片
        '''
        start = time.time()
        if not os.path.exists(self.output_path): os.mkdir(self.output_path)
        for video_name in os.listdir(self.cuted_video_path):
            video_file = os.path.join(self.cuted_video_path, video_name)
            outPutDirName = os.path.join(self.output_path, video_name[:-4])
            VE.extract_video2imgs(video_file, outPutDirName)
            # threading.Thread(target=VE.extract_video2imgs, args=(video_file, outPutDirName)).start()#多线程
        self.num_extract_video = f"共用时{time.time() - start:.2f}s，抽取{len(os.listdir(self.cuted_video_path))}个视频"
        # threading.Thread.join()

    def select_delt_img_1(self, path):#随机删除 核心算法
        #path 是存放抽取过的文件夹地方
        lst = os.listdir(path)
        feed = random.randint(self.al11, self.al12)
        select = int((1-feed/100)*len(lst)) #选择图片数量 1-不选的百分比
        # print(f"随机数是{feed/100:.2f}\n从{len(lst)}张图片，挑选{select}张")
        res = random.sample(lst, select)
        res.sort()
        self.num_del_imgs = self.num_del_imgs + (len(lst)-len(res)) #记录删了多少张图片
        return res

    def select_delt_img_2(self, path): #间隔多少帧率删几张
        lst = os.listdir(path)
        times, count = random.randint(self.al11, self.al12), 0
        for i in lst:
            times+=1
            feed = random.randint(self.al11, self.al12)
            if times%feed ==0:#  dang 10-20 帧张时候随机删一张
                lst.remove(i)
                count += 1
        # print(f"从{len(lst)}里删除{count}张，剩下{len(lst)}张")
        self.num_del_imgs += count
        lst.sort()
        return lst

    def moveimg(self,img_dir=None, res_lst=None):
        '''
        将挑选好的帧数移动到 fuseSpace 准备融合
        :param img_dir: 图片的位置
        :param res_lst: 挑选好的文件 是list
        :return:
        '''
        path_ = Path(self.fuse_path)
        path_.mkdir(exist_ok=True)
        try:
            imgs = os.listdir(self.fuse_path)
            imgs.sort(key=lambda x: int(x[:-4]))  ## 解决图片乱序的问题
            count = int(Path(imgs[-1]).stem)+1
        except IndexError:
             count = 0 # 刚开始运转所以第一个文件是空的
        # print(count)
        for img  in res_lst:
            img_path = PurePath(img_dir,img)
            suff = img_path.suffix#文件后缀
            move_path = PurePath(self.fuse_path,f"{str(count).zfill(5)}{suff}") # 多加00防止乱序
            shutil.copy(img_path,move_path)
            count+=1
            # print(img_path, move_path)

    def random_delt_img(self):
        '''
        用于抽帧
        :param imgs_dir: 存放每个 视频图片的文件夹
        :param self.algorithm: 采用哪种算法
        :return:
        '''
        imgs_dir = self.output_path
        start = time.time()
        for file in  os.listdir(imgs_dir):
            file_path = os.path.join(imgs_dir,file)
            result_lst =None
            if str(self.algorithm) == "1":
                result_lst = self.select_delt_img_1(file_path)
            elif str(self.algorithm) == "2":
                result_lst = self.select_delt_img_2(file_path) #选择算法
            if result_lst:
                self.moveimg(img_dir=file_path, res_lst=result_lst)
            else:
                raise ValueError("算法出错,/nresult_lst{}".format(result_lst))

        self.num_move_img = f"共用时{time.time() - start:.2f}s，移动{len(os.listdir(self.fuse_path))}张图像准备融合视频"

    def img2video(self):
        reference = self.check_path(base_name=self.video_path,  file_name="1") #参考文件
        VE.fuse_img2video_out(input_path=self.fuse_path,
                              output_path=self.output_file,
                              reference_video_path=reference)

    def add_audio_in_video(self):
        files = os.listdir(self.audio_path)
        if len(files)> 0: # 如果音频空间里存放视频
            temp = self.base + "temp.mp4"
            audio = os.path.join(self.audio_path, files[0])
            VE.add_audio(video_path=self.output_file,
                         audio_path=audio,
                         output_path=temp)
            Path(self.output_file).unlink()
            Path(temp).rename(self.output_file)


    def clean(self,path_lst):
        """

        :type pathlst: list
        """
        for path in path_lst:
            shutil.rmtree(path)
            os.mkdir(path)
        print("文件夹清空完成")

    def show_result(self,start_time):
        print(Path.cwd())
        # print(self.sum_cut)
        # print(self.num_extract_video)
        # print(self.num_del_imgs)
        # print(self.num_move_img)
        # print(" ")
        # text = "信息"
        # print(f"{text:-^40}")
        text = "信息总汇"
        print(f"{text:^35}")
        print("-"*40)
        print("{:<10s}{:>20s}".format("状态", "视频融合完成"))
        print("{:<10s}{:>20s}".format("采用算法", str(self.algorithm)))
        frame = "{}-{}".format( self.al11, self.al12)
        print("{:<10s}{:>20s}".format("随机抽取帧率",frame))
        print("-"*40)
        # t = f"{(time.time() - start_time):.0f}" + "秒"
        print("{:<10s}{:>20.2f}秒".format("用时",(time.time() - start_time)))

        # delt = str(self.num_del_imgs) + "帧"
        print("{:<10s}{:>20d}帧".format("删去帧数", self.num_del_imgs))

        # left = str(len(os.listdir(self.fuse_path))) + "帧"
        print("{:<10s}{:>20d}帧".format("剩余帧数",len(os.listdir(self.fuse_path))))

        # cut = str(len(os.listdir(self.cuted_video_path)))+"个"
        print("{:<10s}{:>20d}个".format("融合视频数",len(os.listdir(self.cuted_video_path))))
        print("-"*40)

    def main(self):
        start = time.time()
        # self.VE.get_video_info(r"F:\Projects\FFmpeg_deal_video\workspace\视频\1.mp4")
        try:
            self.creat_files()
            self.clean([r".\workspace\temp"])
            operator_dct = self.readOperator()  # 读取裁剪要求
            self.trim(operator_dct )  # 裁剪视频
            self.extract_imgs_from_video()  # 提取图片
            self.random_delt_img() #抽帧
            self.img2video() #融合成视频
            self.add_audio_in_video()
            self.show_result(start)
            print('')
            key = input('按任意键键退出.....')
            if key:
                sys.exit()
        except:
            traceback.print_exc()
            print("")
            key = input('出错按任意键键退出.....')
            if key:
                sys.exit()


if __name__ == "__main__":
    VideoFuse().main()

