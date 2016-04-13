import pickle
import os
import matplotlib.pyplot as plt
import argparse

# Parse command line agruments
parser = argparse.ArgumentParser(description='Plot log files.')
parser.add_argument('log_dir', type=str, nargs=1, help='log file directory')
args = parser.parse_args()
log_dir = args.log_dir[0]

# Search log files
log_files = os.listdir(log_dir)
log_files = list(filter(lambda x: 'cpu' in x, log_files))

# Lists to store values
list_timestamp  = []
list_cpu_total  = []
list_cpu_kernel = []
list_mem_vm     = []
list_mem_rss    = []
list_sys_cpu    = []
list_sys_mem    = []
list_markers    = []

# Process all logfiles
for log_file in log_files:
    # Open logfile
    filename = "%s/%s" % (log_dir, log_file)
    data = pickle.load(open(filename, 'rb'))
        
    # Retrieve metrics
    timestamp  = [x[0] for x in data] # minutes since epoch 
    cpu_total  = [x[1] for x in data] # %
    cpu_kernel = [x[2] for x in data] # %
    mem_vm     = [x[3] for x in data] # Kb
    mem_rss    = [x[4] for x in data] # Kb
    sys_cpu    = [x[5] for x in data] # %
    sys_mem    = [x[6] for x in data] # Gb
    
    # Convert memory sizes
    mem_vm    = [x / 1024**2 for x in mem_vm] # Kb -> Gb
    mem_rss   = [x / 1024**2 for x in mem_rss] # Kb -> Gb
    sys_mem   = [x / 1024**2 for x in sys_mem] # Kb -> Gb
    
    # Store values
    list_timestamp.append(timestamp)
    list_cpu_total.append(cpu_total)
    list_cpu_kernel.append(cpu_kernel)
    list_mem_vm.append(mem_vm)
    list_mem_rss.append(mem_rss)
    list_sys_cpu.append(sys_cpu)
    list_sys_mem.append(sys_mem)
    list_markers.append(timestamp[0])
   
# Collapse lists    
all_timestamp  = sum(list_timestamp, [])
all_cpu_total  = sum(list_cpu_total, [])
all_cpu_kernel = sum(list_cpu_kernel, [])
all_mem_vm     = sum(list_mem_vm, [])
all_mem_rss    = sum(list_mem_rss, [])
all_sys_cpu    = sum(list_sys_cpu, [])
all_sys_mem    = sum(list_sys_mem, [])

# Start timestamps from 0
all_timestamp = [round(x - all_timestamp[0], 2) for x in all_timestamp]
all_markers = [(x - list_markers[0]) for x in list_markers]

# Convert time to minutes
all_timestamp = [ x / 60 for x in all_timestamp ]
all_markers = [ x / 60 for x in all_markers]

# Remove first marker
all_markers = all_markers[1:]

# Scale CPU percentage to 100%
nr_cpu_cores=1
all_sys_cpu= [ round(x / (nr_cpu_cores), 2) for x in all_sys_cpu]
all_cpu_total = [ round(x / (nr_cpu_cores), 2) for x in all_cpu_total]

# Plot colors
y1_color="blue"
y2_color="green"
x_label="Time (minutes)"
y1_label="CPU usage (%)"
y2_label="Memory usage (Gb)"
marker_color="red"
line_width=2.5
line_width_marker=3.5

# Plot left y-axis
fig, ax1 = plt.subplots()
ax1.plot(all_timestamp, all_sys_cpu, label=y1_label, color=y1_color, linewidth=line_width)
ax1.set_xlabel(x_label)
ax1.set_ylabel(y1_label)
for tl in ax1.get_yticklabels():
    tl.set_color(y1_color)

# Plot right y-axis
ax2 = ax1.twinx()
ax2.plot(all_timestamp, all_sys_mem, label=y2_label, color=y2_color, linewidth=line_width)
ax2.set_ylabel(y2_label)
for tl in ax2.get_yticklabels():
    tl.set_color(y2_color)

# Add markers
for marker in all_markers:
    ax1.plot((marker,marker), (0, 100), color=marker_color, linewidth=line_width_marker)

# Change font size
font_size = 16
axes = (ax1, ax2)
for ax in axes:
    for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] +
                 ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontsize(font_size)

# Show plot
plt.show()
