 
def spectrum(mpath):
    freqx = tfs.read("/media/awegsche/HDD/files/learning/68_omc3_test/output/lin_files/meas_file1.sdds.freqsx")
    ampx = tfs.read("/media/awegsche/HDD/files/learning/68_omc3_test/output/lin_files/meas_file1.sdds.ampsx")

    freqmeas = tfs.read(mpath + ".sdds.freqsx")
    ampmeas = tfs.read(mpath + ".sdds.ampsx")

    fig = plt.figure(figsize=fig_size)
    ax=plt.gca()

    ax.set_yscale("log")
    ax.stem(freqmeas[bpm_name], ampmeas[bpm_name], markerfmt="o", basefmt='', linefmt='gray')
    ax.set_ylim(1.0e-5, 1)
    ax.set_xlabel(r"frequency [$2\pi$]")
    ax.set_ylabel(r"amplitude relative to $Q_x$")

    fig.tight_layout()
    return fig
