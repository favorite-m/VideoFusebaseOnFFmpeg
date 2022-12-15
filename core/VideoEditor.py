import subprocess
import ffmpeg
from core import pathex
from pathlib import Path


#帧率更改 avfilter
def check_ffmpeg():
    stream = ffmpeg.input('input.mp4')
    stream = ffmpeg.hflip(stream)
    stream = ffmpeg.output(stream, 'output.mp4')
    ffmpeg.run(stream)
def print_args(*args,**kwargs):
    print(args)
    print(" ")
    print(kwargs)

def extract_video2imgs(input_file, output_dir, output_ext="png", fps=0):
    input_file_path = Path(input_file)
    output_path = Path(output_dir)

    if not output_path.exists():
        output_path.mkdir(exist_ok=True)

    if input_file_path.suffix == '.*':
        input_file_path = pathex.get_first_file_by_stem (input_file_path.parent, input_file_path.stem)
    else:
        if not input_file_path.exists():
            input_file_path = None

    if fps is None:fps=0
        # fps = io.input_int ("Enter FPS", 0, help_message="How many frames of every second of the video will be extracted. 0 - full fps")

    if output_ext is None: output_ext = "png"
        # output_ext = io.input_str ("Output image format", "png", ["png","png"], help_message="png is lossless, but extraction is x10 slower for HDD, requires x10 more disk space than png.")

    for filename in pathex.get_image_paths (output_path, ['.'+output_ext]):
        Path(filename).unlink()

    job = ffmpeg.input(str(input_file_path))

    kwargs = {'pix_fmt': 'rgb24'}
    if fps != 0:
        kwargs.update ({'r':str(fps)})

    if output_ext == 'png':
        kwargs.update ({'q:v':'2'}) #highest quality for png

    job = job.output( str (output_path / ('%5d.'+output_ext)), **kwargs )
    try:
        job = job.run()
    except:
        print("ffmpeg fail, job commandline:" + str(job.compile()) )

def get_reference_video_fps(reference_file_path):
    # 获取参考视频的帧率
    video_id = None
    audio_id = None
    ref_in_a = None
    probe = ffmpeg.probe(str(reference_file_path))
    # getting first video and audio streams id with fps
    for stream in probe['streams']:
        if video_id is None and stream['codec_type'] == 'video':
            video_id = stream['index']
            # fps = stream['r_frame_rate']
            fps = int(stream['r_frame_rate'].split('/')[0]) / int(stream['r_frame_rate'].split('/')[1])
            return fps

def fuse_img2video_out(input_path=None, audio_path=None,output_path=None, reference_video_path=None):### 不用原视频音频
    '''
    将图片融合成视频
    :param input_path: fuse 用图片的位置
    :param audio_path: fuse 用音频的位置
    :param output_path: 文件保存的位置 r"F:\Projects\data\test\4.mp4
    :param reference_video_path: 参考视频的位置
    :return:
    '''
    if reference_video_path:
        fps = get_reference_video_fps(reference_video_path)
    else: fps= 60
    # print(f"fps是{fps}")
    i_in = ffmpeg.input('pipe:', format='image2pipe', r=fps)
    output_args = [i_in]
    if audio_path:
        au_p = ffmpeg.input(filename=audio_path).audio#.filter('adelay', "1500|1500"
        output_args += [au_p]
    output_args += [str(output_path)]
    output_kwargs = {}
    output_kwargs.update({"c:v": "libx264",
                          "crf": "23",
                          "pix_fmt": "yuv420p",
                          })#loss
    output_kwargs.update({"c:a": "aac",
                          "b:a": "192k",
                          "ar": "48000",
                          "strict": "experimental"
                          })#audio 参数
    input_image_paths = pathex.get_image_paths(input_path)
    # print_args(*output_args, **output_kwargs)
    job = (ffmpeg.output(*output_args, **output_kwargs).overwrite_output())
    job_run = job.run_async(pipe_stdin=True)

    for image_path in input_image_paths:
        with open(image_path, "rb") as f:
            image_bytes = f.read()
            job_run.stdin.write(image_bytes)

    job_run.stdin.close()
    job_run.wait()
    # print("ffmpeg fail, job commandline:" + str(job.compile()))

def trim_video(input_path, output_path, start=30, end=60):
    input_stream = ffmpeg.input(input_path)

    vid = (
        input_stream.video
        .trim(start=start, end=end)
        .setpts('PTS-STARTPTS')
    )
    aud = (
        input_stream.audio
        .filter_('atrim', start=start, end=end)
        .filter_('asetpts', 'PTS-STARTPTS')
    )

    joined = ffmpeg.concat(vid, aud, v=1, a=1).node
    output = ffmpeg.output(joined[0], joined[1], output_path).overwrite_output()
    output.run()

def exctract_audio_from_video(video_path, outputfile):
    audio_input = ffmpeg.input(video_path)
    audio_cut = audio_input.audio
    audio_output = ffmpeg.output(audio_cut, outputfile).overwrite_output()
    ffmpeg.run(audio_output)

def trim_audio(path, outputfile, start,end):
    audio_input = ffmpeg.input(path)
    audio_cut = audio_input.audio.filter('atrim', start=start, end=end)
    print(path,outputfile)
    audio_output = ffmpeg.output(audio_cut, outputfile).overwrite_output()
    ffmpeg.run(audio_output)

def input_type(path):
    #确定输入是视频还是音频
    pass

    # return ffmpeg.probe(path)['streams'][0]["codec_type"]

def add_audio(video_path, audio_path, output_path):
    """
    :param video_path: 想要融合的视频
    :param audio_path: 想要使用音频的 视频或者音频
    :param output_path: 储存路径
    :return:
    """
    v = ffmpeg.probe(video_path)
    a = ffmpeg.probe(audio_path)
    duration_v = v["streams"][0]["duration"]
    duration_a = a["streams"][0]["duration"]


    temp_path = None
    if float(duration_a) > float(duration_v): ##音频比视频长
        cut_ = float(duration_a) - float(duration_v)
        path_ = Path(audio_path)
        name_ = "temp" + ".flac"# 临时文件名字
        temp_path = str(Path.joinpath(path_.parent, name_)) #暂时存放音频的位置 地址记得转换成str
        # print(audio_path,temp_path)
        trim_audio(audio_path,temp_path, 0, cut_)

    vid = ffmpeg.input(video_path).video
    if temp_path is None: #如果存在 音频
        aud = ffmpeg.input(audio_path).audio
    else:
        aud = ffmpeg.input(temp_path).audio
    joined = ffmpeg.concat(vid, aud, v=1, a=1).node
    ffmpeg.output(joined[0], joined[1], output_path).overwrite_output().run()
    if temp_path:Path(temp_path).unlink()



def get_video_info(source_video_path):
    probe = ffmpeg.probe(source_video_path)
    print('source_video_path: {}'.format(source_video_path))
    format = probe['format']
    bit_rate = int(format['bit_rate'])/1000
    duration = format['duration']
    size = int(format['size'])/1024/1024
    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    if video_stream is None:
        print('No video stream found!')
        return
    width = int(video_stream['width'])
    height = int(video_stream['height'])
    num_frames = int(video_stream['nb_frames'])
    fps = int(video_stream['r_frame_rate'].split('/')[0])/int(video_stream['r_frame_rate'].split('/')[1])
    duration = float(video_stream['duration'])

    print("Video statistics:")
    print("  ----------------------------------------")
    print("  Items      | Info ")
    print("  ----------------------------------------")
    print("  Path       | {:>20s}  ".format(str(source_video_path)))
    print("  width      | {:20d} ".format(width) )
    print("  height     | {:20d} ".format(height) )
    print("  num_frames | {:20d} ".format(num_frames) )
    print("  fps        | {:>20.0f} fps ".format(fps) )
    print("  duration   | {:>20.0f} s ".format(duration))
    print("  size       | {:>20.0f} MB ".format(size))
    print("  bit_rate   | {:>20.0f} k ".format(bit_rate))
    print("  ----------------------------------------")



if __name__ == "__main__":
    a = r"F:\Projects\FFmpeg_deal_video\workspace\\融合的视频.mp4"
    a2 = r"F:\Projects\FFmpeg_deal_video\workspace\音频\\1.mp4"
    a3 = r"F:\Projects\FFmpeg_deal_video\workspace\xxx.mp4"
    add_audio(a,a2, a3)
    # get_video_info(a2)
    # # probe = ffmpeg.probe(a2)
    # trim_audio(a222, r"F:\Projects\FFmpeg_deal_video\workspace\temp.flac", 0,"5")
    # print(probe["streams"][0]["duration"])
    # x = ffmpeg.input(a).audio.filter("silencedetect",noise=0.0001)
    # print(x)
    # input_dir = r"F:\Projects\data\test\fuse"
    # output_file = r"F:\Projects\data\test\fuse_test1.mp4"
    # audio_path = r"F:\Projects\data\test\e.mp3"
    # RF = r"F:\Projects\data\test\er.*"
    # mp3 = r"F:\Projects\data\test\eee.mp3"
    # tes =  r"F:\Projects\data\test\4.mp4"
    # get_video_info(tes)
    # fuse_img2video_out(input_dir,audio_path,output_file)
    # exctract_audio_from_video(tes,mp3,30,60)
    # VG.fuse_img_2_video(input_dir=input_dir,output_file=output_file,reference_file=RF,lossless=True)
    # fuse_audio(input_path=input_dir, audio_path=audio_path, output_path=output_file)
    # probe = ffmpeg.probe(str(RF))
    # for stream in probe["streams"]:
    #     print(str(stream))

