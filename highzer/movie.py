from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip


def concat_clips(files, out_file):
    clips = list()
    for i, file in enumerate(files):
        clip = VideoFileClip(file).resize((1920, 1080)) \
            .crossfadeout(1).crossfadein(1)

        # rank = TextClip(f"# {5 - i}", fontsize=150, color='white', font='Times New Roman') \
            # .set_duration(4).set_position('center').set_start(1) \
            # .crossfadein(1).crossfadeout(2)

        comp = CompositeVideoClip([clip])

        clips.append(comp)

    final_clip = concatenate_videoclips(clips, method="chain")
    final_clip.write_videofile(out_file)


if __name__ == '__main__':
    files = ['small.mp4', 'mid.mp4', 'large.mp4']
    concat_clips(files, 'out.mp4')
