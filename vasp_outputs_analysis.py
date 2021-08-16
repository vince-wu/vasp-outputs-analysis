from paramiko import SSHClient, AutoAddPolicy
from pymatgen.io.vasp.inputs import Incar
from pymatgen.io.vasp.outputs import Oszicar, Vasprun
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
from pathlib import Path
import numpy as np
import os

BASE_DIR = 'c:/Users/Vincent/Box/Clement Research/VASP/'

def parse_output(vasprun_filename, oszicar_filename, incar_filename):
    vasp_run = Vasprun(vasprun_filename, exception_on_bad_xml=False)
    oszicar = Oszicar(oszicar_filename)
    incar = Incar.from_file(incar_filename)
    
    print("Files successfull parsed")
    print("------------------------------------------------------------")
    incar_dict = incar.as_dict()
    # print(incar_dict)
    if 'EDIFF' in incar_dict:
        incar_ediff = incar_dict['EDIFF']
    else:
        incar_ediff = 10e-4
    if 'EDIFFG' in incar_dict:
        incar_ediffg = incar_dict['EDIFFG']
    else:
        incar_ediffg = incar_ediff*10

    oszicar_esteps = oszicar.electronic_steps
    oszicar_ionic_steps = oszicar.ionic_steps

    # Get ionic step information
    ediff = [x['dE'] for x in oszicar_ionic_steps]
    abs_ediff = [abs(x) for x in ediff]
    final_ediff = ediff[-1]

    # Get electronic step infomation for last ionic step
    final_ionic_step_esteps = [x['dE'] for x in oszicar_esteps[-1]]
    abs_final_ionic_step_esteps = [abs(x) for x in final_ionic_step_esteps]
    num_esteps = len(final_ionic_step_esteps)
    final_estep_ediff = final_ionic_step_esteps[-1]
    
    num_ionic_steps = vasp_run.nionic_steps
    fermi_energy = vasp_run.efermi
    final_energy = vasp_run.final_energy
    ionic_steps = range(num_ionic_steps)
    print("Number of ionic steps: {}".format(num_ionic_steps))
    print("Fermi energy (eV): {}".format(fermi_energy))
    print("Final energy (eV): {}".format(final_energy))
    print("Final ionic step dE (eV): {}".format(final_ediff))
    print("Final electronic step dE (eV): {}".format(final_estep_ediff))
    free_energy = [x['e_fr_energy'] for x in vasp_run.ionic_steps]
    electronic_steps = [[x['electronic_steps']] for x in vasp_run.ionic_steps]
    last_estep = electronic_steps[-1][0]
    # print(last_estep)
    last_estep_energies = [x['e_fr_energy'] for x in last_estep]
    # print(electronic_steps[1][0])
    num_electronic_steps = [len(x[0]) for x in electronic_steps]
    # print(vasp_run.ionic_steps[0])


    # plot parameters
    plt.rcParams.update({'font.size': 14})
    plt.rcParams.update({'font.family':'Arial'})
    # plot size
    # plt.figure(figsize=(14,12))
    # font size for x- and y- axis labels
    fsize = 14
    fig = plt.figure(figsize=(10,8))
    ax1 = plt.subplot(221)
    ax2 = plt.subplot(222)
    ax3 = plt.subplot(223)
    ax4 = plt.subplot(224)

    fig.figsize = (1,12)
    ax1.plot(free_energy, 'o-',  linewidth=3)
    ax1.set_xlabel('Ionic step #', fontsize=fsize)
    ax1.set_ylabel('Free energy (eV)', fontsize=fsize)

    ax2.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax2.plot(ionic_steps, num_electronic_steps, '-o',  linewidth=3)
    ax2.set_xlabel('Ionic step #', fontsize=fsize)
    ax2.set_ylabel('# of electronic steps', fontsize=fsize)

    ax3.axhline(incar_ediffg, color='r', label='ediffg')
    ax3.semilogy(ionic_steps, abs_ediff, '-o', linewidth=3)
    ax3.set_xlabel('Ionic step #', fontsize=fsize)
    ax3.set_ylabel('abs(energy diff) for ionic step (eV)', fontsize=fsize)
    ax3.legend()

    ax4.ticklabel_format(useOffset=False)
    ax4.axhline(incar_ediff, color='r', label='ediff')
    ax4.semilogy(range(num_esteps), abs_final_ionic_step_esteps, '-o',  linewidth=3)
    ax4.set_xlabel('Electronic step # for last ionic step', fontsize=fsize)
    ax4.set_ylabel('abs(energy diff) for electronic step (eV)', fontsize=fsize)
    ax4.legend()

    fig.tight_layout(pad=1.5)
    plt.show()

def get_remote_dir(username, server, password, remote_dir, local_dir):
    """
    DESCRIPTION: 
    PARAMETERS:
    RETURNS:
    """
    client = SSHClient()
    client.load_system_host_keys()
    client.connect(server, username=username, password=password)
    ftp_client = client.open_sftp()

    Path(local_dir).mkdir(parents=True, exist_ok=True)

    incar_file_remote = None
    incar_file_local = None

    poscar_file_remote = None
    poscar_file_local = None

    potcar_file_remote = None
    potcar_file_local = None

    kpoints_file_remote = None
    kpoints_file_local = None

    contcar_file_remote = None
    contcar_file_local = None

    chgcar_file_remote = None
    chgcar_file_local = None

    doscar_file_remote = None
    doscar_file_local = None

    vaspjob_file_remote = None
    vaspjob_file_local = None

    outcar_file_remote = None
    outcar_file_local = None

    oszicar_file_remote = None
    oszicar_file_local = None

    vasprun_file_remote = None
    vasprun_file_local = None

    for file in ftp_client.listdir(remote_dir):
        print(file)
        if "incar" in file.lower():
            incar_file_remote = remote_dir + file
            incar_file_local = local_dir + file
        elif "poscar" in file.lower():
            poscar_file_remote = remote_dir + file
            poscar_file_local = local_dir + file
        elif "potcar" in file.lower():
            potcar_file_remote = remote_dir + file
            potcar_file_local = local_dir + file
        elif "kpoints" in file.lower():
            kpoints_file_remote = remote_dir + file
            kpoints_file_local = local_dir + file
        elif "contcar" in file.lower():
            contcar_file_remote = remote_dir + file
            contcar_file_local = local_dir + file
        elif "chgcar" in file.lower():
            chgcar_file_remote = remote_dir + file
            chgcar_file_local = local_dir + file
        elif "doscar" in file.lower():
            doscar_file_remote = remote_dir + file
            doscar_file_local = local_dir + file
        elif "vasp-job" in file.lower():
            vaspjob_file_remote = remote_dir + file
            vaspjob_file_local = local_dir + file
        elif "outcar" in file.lower():
            outcar_file_remote = remote_dir + file
            outcar_file_local = local_dir + file
        elif "oszicar" in file.lower():
            oszicar_file_remote = remote_dir + file
            oszicar_file_local = local_dir + file
        elif "vasprun" in file.lower():
            vasprun_file_remote = remote_dir + file
            vasprun_file_local = local_dir + file
    remote_paths = [incar_file_remote, poscar_file_remote, potcar_file_remote, kpoints_file_remote, contcar_file_remote, chgcar_file_remote,
    doscar_file_remote, vaspjob_file_remote, outcar_file_remote, oszicar_file_remote, vasprun_file_remote]
    local_paths = [incar_file_local, poscar_file_local, potcar_file_local, kpoints_file_local, contcar_file_local, chgcar_file_local,
    doscar_file_local, vaspjob_file_local, outcar_file_local, oszicar_file_local, vasprun_file_local]

    # get file size of OUTCAR
    print(outcar_file_remote)
    file_stat = ftp_client.lstat(outcar_file_remote)
    file_size_kB = file_stat.st_size/1024
    print("OUTCAR file size: {} kB".format(np.round(file_size_kB,2)))

    # if file size is too large, do not download OUTCAR, as something likely went wrong with the relaxation
    if file_size_kB > 200000:
        Exception("OUTCAR file size is very large, there may be a problem with the relaxation. Output files will not be downloaded.")

    # transfer all remote data files to local storage
    for remote_path, local_path in zip(remote_paths, local_paths):
        print('remote: ', remote_path)
        print('local: ', local_path)
        ftp_client.get(remote_path, local_path)
    ftp_client.close()
    client.close()

# ssh details
username = 'vincentwu'
server = 'braid.cnsi.ucsb.edu'
password = None # have ssh key, no need for password
# server = 'pod.cnsi.ucsb.edu'

# define remote directory to read from
remote_path = 'alluaudite-project/Na2Mn3VO4_3/GGA_U/relax1/'

# define local directory to copy to
local_path = BASE_DIR + 'alluaudite-project/Na2Mn3VO4_3/GGA_U/'

# define local filenames for INCAR, OSZICAR, and vasprun to parse
vasprun_name = 'vasprun.xml'
oszicar_name = 'OSZICAR'
incar_name = 'INCAR'
vasprun_file = local_path + vasprun_name
oszicar_file = local_path + oszicar_name
incar_file = local_path + incar_name

# copy data files from remote server to local machine
get_remote_dir(username, server, password, remote_path, local_path)
# parse the output files that are on the local machine
parse_output(vasprun_file, oszicar_file, incar_file)