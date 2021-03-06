import matplotlib.gridspec as gridspec
import numpy as np

from matplotlib import cm
from matplotlib import pyplot as mplt
from matplotlib import patheffects as mpe
from matplotlib.patches import Circle, Wedge, Rectangle
from matplotlib.ticker import MultipleLocator, FormatStrFormatter  
from matplotlib.animation import FuncAnimation
#from matplotlib.axes import Axes

def visual_setup():
    mplt.ion()
    return

def visual_teardown():
    mplt.ioff()
    mplt.show()
    return

'''
def update_line(num, data, line):
    # step is 1ms
    start_time = num*1e-3
    end_time = num*1e-3+1.0
    #print("from time", start_time, "to time", end_time)
    data_seq = [d for d in data if start_time <= d[0] < end_time]
    x_data = [d[0]-start_time for d in data_seq]
    y_data = [d[1] for d in data_seq]
    line.set_data(x_data, y_data)
    return line,
    
def draw_timed_sequence_animation(data_list):
    scr_dpi, style = 96, 'seaborn-white'
    fig = mplt.figure(figsize=(300/scr_dpi, 300/scr_dpi), dpi=scr_dpi)
    mplt.style.use(style)

    mplt.title("Speed (Kmph)", fontsize=10, fontweight=0, color='grey', loc='left')
    mplt.xlabel('Time')
    mplt.tick_params(labelbottom=False)
    mplt.ylabel('Speed (Km/H)')
    mplt.tick_params(labelleft=True)

    #data = np.random.rand(2, 15)
    l, = mplt.plot([],[])
    mplt.xlim(0, 1)
    mplt.ylim(-10, 180)
    l.tick_params(labelbottom=False, labelleft=True)
    
    frames = int((data_list[-1][0]-1.0)*1e3)
    return FuncAnimation(fig, update_line, frames, fargs=(data_list, l), interval=2, blit=True)
'''

def update_line(num, data_src, lines):
    # step is 1ms
    start_time = num*1e-3
    end_time = num*1e-3+3.0

    for i in range(len(data_src)):
        data_seq = [d for d in data_src[i] if start_time<=d[0]<end_time]
        x_data = [d[0]-start_time for d in data_seq]
        y_data = [d[1] for d in data_seq]
        lines[i].set_data(x_data, y_data)
        #lines[i].set_color('red')

    return lines

def draw_animation(data_src):
    scr_dpi, style = 96, 'seaborn-white'
    fig = mplt.figure(figsize=(900/scr_dpi, 300/scr_dpi), dpi=scr_dpi)
    #mplt.style.use(style)
    ax0, ax1, ax2 = mplt.subplot(1,3,1), mplt.subplot(1,3,2), mplt.subplot(1,3,3) 

    ax0.set_xlim(0,3)
    ax0.set_ylim(-10,180)
    ax0.set_title('Speed [kmph]', fontsize=10, fontweight=0, color='grey', loc='left')
    ax0.grid(True)

    ax1.set_xlim(0,3)
    ax1.set_ylim(-10,6000)
    ax1.set_title('Engine Speed [RPM]', fontsize=10, fontweight=0, color='grey', loc='left')
    ax1.grid(True)

    ax2.set_xlim(0,3)
    ax2.set_ylim(-10,260)
    ax2.set_title('Torque [N-m]', fontsize=10, fontweight=0, color='grey', loc='left')
    #ax2.spines['top'].set_color('red')
    #ax2.spines['right'].set_visible(False)
    ax2.grid(True)

    path_eff = [mpe.SimpleLineShadow(shadow_color='b'), mpe.Normal()]
    l1, = ax0.plot([],[], color='mediumvioletred', linewidth=3, path_effects=path_eff)
    l2, = ax1.plot([],[], color='mediumvioletred', linewidth=3, path_effects=path_eff)
    l3, = ax2.plot([],[], color='mediumvioletred', linewidth=3, path_effects=path_eff)

    data_samp = data_src[0]
    frames = int((data_samp[-1][0]-3.0)*1e3)

    lines = (l1,l2,l3)
    return FuncAnimation(fig, update_line, frames, fargs=(data_src, lines), interval=1, blit=True)

def draw_timed_sequence(data_list, title, data_range):
    # customize figure properties
    scr_dpi, style = 96, 'seaborn-white'
    mplt.figure(figsize=(800/scr_dpi, 300/scr_dpi), dpi=scr_dpi)
    mplt.style.use(style)

    # drow speed curves
    time_seq = [i[0] for i in data_list]
    data_seq = [i[1] for i in data_list]
    mplt.plot(time_seq, data_seq, marker='', color='mediumvioletred', \
                linewidth=3, alpha=1, \
                path_effects=[mpe.SimpleLineShadow(shadow_color='b'), mpe.Normal()])

    mplt.title(title, fontsize=10, fontweight=0, color='grey', loc='left')
    mplt.grid(True)

    # set x-axis properties
    xmajorLocator   = MultipleLocator(2)
    xmajorFormatter = FormatStrFormatter('%1d')
    ax = mplt.gca()
    ax.xaxis.set_major_locator(xmajorLocator)  
    ax.xaxis.set_major_formatter(xmajorFormatter)  
    
    # set y-axis properties
    mplt.ylim(data_range)

    #mplt.xlabel('Time (Second)')
    #mplt.tick_params(labelbottom=True)
    #mplt.ylabel('Speed (Km/H)')
    #mplt.tick_params(labelleft=True)

def draw_speedometer(speedometer_record):
    # customize figure properties
    scr_dpi, style = 96, 'seaborn-white'
    mplt.figure(1, figsize=(1200/scr_dpi, 300/scr_dpi), dpi=scr_dpi)
    mplt.style.use(style)
    gs = gridspec.GridSpec(1,2, width_ratios=[2,1])
    mplt.subplot(gs[0])

    # drow speed curves
    time = [i[0] for i in speedometer_record]
    speed = [i[1] for i in speedometer_record]
    mplt.plot(time, speed, marker='', color='mediumvioletred', \
                linewidth=2, alpha=1, \
                path_effects=[mpe.SimpleLineShadow(shadow_color='b'), mpe.Normal()])
    # mplt.grid(True)
    # mplt.ylim((-2, 2))
    # mplt.legend(['sine'])
    mplt.title("Speed (Kmph)", fontsize=10, fontweight=0, color='grey', loc='left')
    # remove labels
    mplt.xlabel('Time (Second)')
    mplt.tick_params(labelbottom=True)
    #mplt.ylabel('Speed (Km/H)')
    mplt.tick_params(labelleft=True)
    return

def degree_range(n): 
    start = np.linspace(-45 ,225, n+1, endpoint=True)[0:-1]
    end = np.linspace(-45, 225, n+1, endpoint=True)[1::]
    mid_points = start + ((end-start)/2.)
    return np.c_[start, end], mid_points

def rot_text(ang): 
    rotation = np.degrees(np.radians(ang) * np.pi / np.pi - np.radians(90))
    return rotation

def draw_gauge(axes, value, range, labels=['LOW','MEDIUM','HIGH','VERY HIGH','EXTREME'], colors='jet_r', title=''): 
    N = len(labels)
    """
    if colors is a string, we assume it's a matplotlib colormap
    and we discretize in N discrete colors 
    """
    if isinstance(colors, str):
        cmap = cm.get_cmap(colors, N)
        cmap = cmap(np.arange(N))
        colors = cmap[::-1,:].tolist()
    if isinstance(colors, list): 
        if len(colors) == N:
            colors = colors[::-1]
        else: 
            raise Exception("\n\nnumber of colors {} not equal \
            to number of categories{}\n".format(len(colors), N))
    
    # begins the plotting
    ang_range, mid_points = degree_range(N)
    labels = labels[::-1]
    
    # plots the sectors and the arcs
    patches = []
    for ang, c in zip(ang_range, colors): 
        # sectors
        # patches.append(Wedge((0.,0.), .4, *ang, facecolor='w', lw=2))
        # arcs
        patches.append(Wedge((0.,0.), .4, *ang, width=0.1, facecolor=c, lw=2, alpha=0.5, \
        path_effects=[mpe.withStroke(linewidth=1, foreground="k")]))
    [axes.add_patch(p) for p in patches]

    tick_num = 6
    label_pos = np.linspace(225 ,-45, tick_num, endpoint=True)
    label_txt = [str(int(i)) for i in np.linspace(range[0], range[1], tick_num, endpoint=True)]

    # set the labels (e.g. 'LOW','MEDIUM',...)
    for pos, txt in zip(label_pos, label_txt): 
        axes.text(0.38 * np.cos(np.radians(pos)), 0.38 * np.sin(np.radians(pos)), txt, \
            horizontalalignment='center', verticalalignment='center', fontsize=6, \
            fontweight='normal', rotation = rot_text(pos))

    # set the bottom banner and the title
    r = Rectangle((-0.2,-0.1),0.4,0.1, facecolor='w', lw=2, path_effects=[mpe.withStroke(linewidth=1, foreground="k")])
    axes.add_patch(r)
    axes.text(0, -0.05, title, horizontalalignment='center', \
         verticalalignment='center', fontsize=12, fontweight='bold')

    #plots the arrow now
    # arrow = int(value/10)
    pos = (range[1]-value)*270.0/(range[1]-range[0])-45
    axes.arrow(0, 0, 0.225 * np.cos(np.radians(pos)), 0.225 * np.sin(np.radians(pos)), \
                 width=0.01, head_width=0.02, head_length=0.1, fc='k', ec='k')
    
    axes.add_patch(Circle((0, 0), radius=0.02, facecolor='k'))
    axes.add_patch(Circle((0, 0), radius=0.01, facecolor='w', zorder=11))

    # removes frame and ticks, and makes axis equal and tight
    axes.set_frame_on(False)
    axes.axes.set_xticks([])
    axes.axes.set_yticks([])
    axes.axis('equal')
    mplt.tight_layout()