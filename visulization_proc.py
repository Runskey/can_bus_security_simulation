import matplotlib.gridspec as gridspec
import numpy as np

from matplotlib import cm
from matplotlib import pyplot as mplt
from matplotlib import patheffects as mpe
from matplotlib.patches import Circle, Wedge, Rectangle
#from matplotlib.axes import Axes

def visual_setup():
    mplt.ion()
    return

def visual_teardown():
    mplt.ioff()
    mplt.show()
    return

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
    mplt.tick_params(labelbottom=False)
    #mplt.ylabel('Speed (Km/H)')
    mplt.tick_params(labelleft=True)

    # draw speedometer gauge
    axes = mplt.subplot(gs[1])
    draw_gauge(speedometer_record[-1][1], axes, labels=[str(i) for i in range(10, 180, 10)], colors='jet_r', title='Speedometer')
    return

    #gauge(speedometer_record, labels=['LOW','MEDIUM','HIGH','VERY HIGH','EXTREME'], colors='jet_r', arrow=1, title='Speedometer', fname=False)
    #gauge(speedometer_record, labels=[str(i) for i in range(10, 180, 10)], colors='jet_r', title='Speedometer')

def draw_tachometer(tachometer_record):
    # customize figure properties
    scr_dpi, style = 96, 'seaborn-white'
    mplt.figure(2, figsize=(1200/scr_dpi, 300/scr_dpi), dpi=scr_dpi)
    mplt.style.use(style)
    gs = gridspec.GridSpec(1,2, width_ratios=[2,1])
    mplt.subplot(gs[0])

    # drow speed curves
    time = [i[0] for i in tachometer_record]
    tach = [i[1] for i in tachometer_record]
    mplt.plot(time, tach, marker='', color='mediumvioletred', \
                linewidth=2, alpha=1, \
                path_effects=[mpe.SimpleLineShadow(shadow_color='b'), mpe.Normal()])
    # mplt.grid(True)
    # mplt.ylim((-2, 2))
    # mplt.legend(['sine'])
    mplt.title("RPM", fontsize=10, fontweight=0, color='grey', loc='left')
    # remove labels
    mplt.xlabel('Time (Second)')
    mplt.tick_params(labelbottom=False)
    #mplt.ylabel('Speed (Km/H)')
    mplt.tick_params(labelleft=True)

    # draw speedometer gauge
    axes = mplt.subplot(gs[1])
    draw_gauge(tachometer_record[-1][1], axes, labels=[str(i) for i in range(100, 8000, 100)], colors='jet_r', title='Speedometer')
    return

def degree_range(n): 
    start = np.linspace(0,180,n+1, endpoint=True)[0:-1]
    end = np.linspace(0,180,n+1, endpoint=True)[1::]
    mid_points = start + ((end-start)/2.)
    return np.c_[start, end], mid_points

def rot_text(ang): 
    rotation = np.degrees(np.radians(ang) * np.pi / np.pi - np.radians(90))
    return rotation

def draw_gauge(value, axes, labels=['LOW','MEDIUM','HIGH','VERY HIGH','EXTREME'], colors='jet_r', title=''): 
    
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
    """
    begins the plotting
    """
    ang_range, mid_points = degree_range(N)
    labels = labels[::-1]
    
    """
    plots the sectors and the arcs
    """
    patches = []
    for ang, c in zip(ang_range, colors): 
        # sectors
        patches.append(Wedge((0.,0.), .4, *ang, facecolor='w', lw=2))
        # arcs
        patches.append(Wedge((0.,0.), .4, *ang, width=0.10, facecolor=c, lw=2, alpha=0.5))
    [axes.add_patch(p) for p in patches]

    """
    set the labels (e.g. 'LOW','MEDIUM',...)
    """
    for mid, lab in zip(mid_points, labels): 
        axes.text(0.35 * np.cos(np.radians(mid)), 0.35 * np.sin(np.radians(mid)), lab, \
            horizontalalignment='center', verticalalignment='center', fontsize=6, \
            fontweight='normal', rotation = rot_text(mid))

    """
    set the bottom banner and the title
    """
    r = Rectangle((-0.4,-0.1),0.8,0.1, facecolor='w', lw=2)
    axes.add_patch(r)
    axes.text(0, -0.05, title, horizontalalignment='center', \
         verticalalignment='center', fontsize=12, fontweight='bold')

    """
    plots the arrow now
    """
    arrow = int(value/10)
    pos = mid_points[abs(arrow - N)]
    axes.arrow(0, 0, 0.225 * np.cos(np.radians(pos)), 0.225 * np.sin(np.radians(pos)), \
                 width=0.01, head_width=0.02, head_length=0.1, fc='k', ec='k')
    
    axes.add_patch(Circle((0, 0), radius=0.02, facecolor='k'))
    axes.add_patch(Circle((0, 0), radius=0.01, facecolor='w', zorder=11))

    """
    removes frame and ticks, and makes axis equal and tight
    """
    axes.set_frame_on(False)
    axes.axes.set_xticks([])
    axes.axes.set_yticks([])
    axes.axis('equal')
    mplt.tight_layout()
