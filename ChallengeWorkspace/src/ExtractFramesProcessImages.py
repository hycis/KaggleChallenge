import sys, getopt, glob, os, glob
from zipfile import ZipFile
from subprocess import call
from PIL import Image
from datetime import datetime

def removeNoisyBackground(unzipFolder_path, report, resizeDim):
    
    ''' Remove noisy background from the depth images, crop to square, 
        resize and save over the original depth images
    '''
    
    folder_list = glob.glob('{}/*'.format(unzipFolder_path))
    clip_name = unzipFolder_path.split('/')[-1]
    
    print clip_name
    
    depth_frames_path_list = []
    user_frames_path_list = []
    
    for item in folder_list:
        if os.path.isdir(item):
            if 'depth_frames' in item:
                depth_frames_path_list = glob.glob('{}/*.png'.format(item))
            elif 'user_frames' in item:
                user_frames_path_list = glob.glob('{}/*.png'.format(item))
        
    #depth_frames_path_list = ['/Users/zhenzhou/Desktop/KaggleChallenge/data/training1/Sample00007/Sample00007_depth_frames/Sample00007_depth-0029.png']
    #user_frames_path_list = ['/Users/zhenzhou/Desktop/KaggleChallenge/data/training1/Sample00007/Sample00007_user_frames/Sample00007_user-0029.png']
    
    if len(depth_frames_path_list) != len(user_frames_path_list):
        print 'depth frames and user frames size not equal'
        report.write('Error: depth frames and user frames size not equal for: ' + clip_name + '\n')
        return
                
    for i in range(0, len(depth_frames_path_list)):
        depth_im = Image.open(depth_frames_path_list[i])
        user_im = Image.open(user_frames_path_list[i])
        depth_pix = depth_im.load()
        user_pix = user_im.load()
        
        W, H = depth_im.size
        for x in range(0, W):
            for y in range(0, H):
                if sum(user_pix[x,y]) < 100:
                    depth_pix[x,y] = (0,0,0)
        
        # TL : top left
        # BR : bottom right
        x_TL = (W-H)/2
        y_TL = 0
        x_BR = H + (W-H)/2
        y_BR = H - 1
        depth_im.crop((x_TL, y_TL, x_BR, y_BR)).resize((resizeDim, resizeDim)).save(depth_frames_path_list[i])
        
def unzipExtractFramesDepthUser(zipfile):
    
    ''' unzip the zipfile and extract frames from the depth and user clips
    '''
    
    if not os.path.exists(zipfile[:-4]):
        os.mkdir(zipfile[:-4])
    with ZipFile(zipfile) as clips_zip:
        
        for clip in clips_zip.namelist():
            if clip[-3:] == 'mat' or 'mp4' or 'wav':
                clips_zip.extract(clip, zipfile[:-4])
                
                if 'depth' in clip or 'user' in clip:
                    clip_path = '{}/{}'.format(zipfile[:-4], clip)
                    
                    frame_folder_path = '{}/{}{}'.format(zipfile[:-4], clip[:-4], '_frames/' )
                    if not os.path.exists(frame_folder_path):
                        os.mkdir(frame_folder_path)
                    cmd = 'ffmpeg -q 1 -i {} {}{}{}'.format(clip_path, frame_folder_path, clip[:-4], '-%4d.png')
                    call([cmd], shell=True)
        
def main(argv):
    try:
        opts, args = getopt.getopt(argv, 'i:r:')
    except getopt.GetoptError:
        print 'python ExtractFramesProcessImages.py -i <inputfolderForAllZipFiles> -r <reportPath>'
        sys.exit(1)
    if opts[0][0] == '-i':
        folder_path = opts[0][1]
    if opts[1][0] == '-r':
        report_path = opts[1][1]
    
    if folder_path[-1] != '/':
        folder_path += '/'
    
    ziplist = glob.glob(folder_path + '*.zip')
    #ziplist = ['/Users/zhenzhou/Desktop/KaggleChallenge/data/training1/Sample00007.zip']
    
    report = open(report_path, 'a')
    dt = datetime(1,1,1)
    report.write('preprocessing commenced on ' + dt.today().strftime('%d-%b-%Y %H:%M') + '\n')
    
    for zipfile in ziplist:
        
        try:
            unzipExtractFramesDepthUser(zipfile)
            resizeDim = 96
            removeNoisyBackground(zipfile[:-4], report, resizeDim)
            
            report.write("completed successfully for " + zipfile.split('/')[-1] + '\n')

        except:
            print "Unexpected error:", str(sys.exc_info()[1])
            report.write("Unexpected error:" + str(sys.exc_info()[1]) + '\n')
        
    
if __name__ == '__main__':
    main(sys.argv[1:])