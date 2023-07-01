import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import cumulative_trapezoid
import scipy.interpolate as sp


def x_load(nparticles):
    global pos_x, pos_y, v_y, v_x, rho_b
    pos_x = np.random.uniform(0, length, nparticles)
    pos_y = np.random.uniform(0, length, nparticles)
    v_x = np.zeros(nparticles)
    v_y = np.zeros(nparticles)
    if two_stream == 1:
        print('This is streaming simulation')
        vel = float(input('enter the value of streaming velocity: '))
        v_x[int(nparticles/2):] = vel
        v_x[:nparticles - int(nparticles/2)] = -vel
    else:
        print("This is a normal simulation")

    print('The ion are acting as neutralizing background')
    # ion background projection
    rho_b = np.zeros((ngrid + 1) * (ngrid + 1))
    x = np.linspace(0.001, 0.999 * length, int(np.sqrt(nparticles)))
    y = np.linspace(0.001, 0.999 * length, int(np.sqrt(nparticles)))
    a9, b9 = np.meshgrid(x, y)
    a9 = a9.flatten()
    b9 = b9.flatten()
    for i in range(0, nparticles):
        a1 = a9[i] / dx
        a2 = b9[i] / dx
        index_x1 = int(a1)
        index_y1 = int(a2)
        index_grid = index_x1 + ((ngrid + 1) * index_y1)
        f1 = index_grid
        f2 = f1 + 1
        f3 = f1 + (ngrid + 1)
        f4 = f3 + 1
        weight_2x = a1 - index_x1
        weight_1x = 1.0 - weight_2x
        weight_2y = a2 - index_y1
        weight_1y = 1.0 - weight_2y
        rho_b[f1] = rho_b[f1] + (weight_1x * weight_1y)
        rho_b[f2] = rho_b[f2] + (weight_2x * weight_1y)
        rho_b[f3] = rho_b[f3] + (weight_1x * weight_2y)
        rho_b[f4] = rho_b[f4] + (weight_2x * weight_2y)


def projection():
    global pos_x, pos_y, nparticles, rho_t, rho_e
    rho_e = np.zeros((ngrid + 1) * (ngrid + 1))
    # electron projection
    for i in range(0, nparticles):
        a1 = pos_x[i] / dx
        a2 = pos_y[i] / dx
        index_x1 = int(a1)
        index_y1 = int(a2)
        index_grid = index_x1 + ((ngrid + 1) * index_y1)
        f1 = index_grid
        f2 = f1 + 1
        f3 = f1 + (ngrid + 1)
        f4 = f3 + 1
        weight_2x = a1 - index_x1
        weight_1x = 1.0 - weight_2x
        weight_2y = a2 - index_y1
        weight_1y = 1.0 - weight_2y
        rho_e[f1] = rho_e[f1] + (weight_1x * weight_1y)
        rho_e[f2] = rho_e[f2] + (weight_2x * weight_1y)
        rho_e[f3] = rho_e[f3] + (weight_1x * weight_2y)
        rho_e[f4] = rho_e[f4] + (weight_2x * weight_2y)

    # applying boundary condition to the electron distribution
    for i in range(1, ngrid):
        rho_e[i] += rho_e[i + (ngrid+1)*ngrid]
        rho_e[i + (ngrid+1)*ngrid] = rho_e[i]/2
        rho_e[i] = rho_e[i]/2
    for i in range(1, ngrid):
        rho_e[i * (ngrid+1)] += rho_e[i * (ngrid+1) + ngrid]
        rho_e[i * (ngrid + 1) + ngrid] = rho_e[i * (ngrid+1)]/2
        rho_e[i * (ngrid + 1)] = rho_e[i * (ngrid+1)]/2
    rho_e[0] += rho_e[ngrid] + rho_e[((ngrid+1) * (ngrid+1)) - 1] + rho_e[(ngrid+1)*ngrid]
    rho_e[ngrid] = rho_e[0]/4
    rho_e[((ngrid+1) * (ngrid+1)) - 1] = rho_e[ngrid]
    rho_e[(ngrid+1)*ngrid] = rho_e[ngrid]
    rho_e[0] = rho_e[ngrid]

    rho_t = rho_b - rho_e
    return True


def boundary_condition(bc_particle):
    global pos_x, pos_y, length
    # optimise this with boolean operation
    # periodic boundary condition, here direction nor value of velocity change
    if bc_particle == 1:
        a1 = pos_x > length
        pos_x[a1] = pos_x[a1] - length
        a2 = pos_x < 0
        pos_x[a2] = length + pos_x[a2]
        b1 = pos_y > length
        pos_y[b1] = pos_y[b1] - length
        b2 = pos_y < 0
        pos_y[b2] = length + pos_y[b2]

    return True


def electric_field():
    global rho_t, dx, ngrid, E_x, E_y, electric_res, x, var_E, r
    E_y = []
    E_x = []

    # integrating using inbuilt function
    for j in range(0, ngrid + 1):
        a = rho_t[j * (ngrid + 1):(j + 1) * (ngrid + 1)]
        int_a = cumulative_trapezoid(x, a, initial=0)
        # periodic fields: subtract off DC component */
        # -- need this for consistency with charge conservation */
        # sum_ex = np.sum(int_a)
        # int_a -= sum_ex/ngrid
        int_a[0] = int_a[ngrid]
        E_x.append(int_a)
    E_x = np.array(E_x)
    for j in range(0, ngrid + 1):
        e_y = []
        for i in range(0, ngrid + 1):       # this gives me my density array along y
            a = rho_t[j + i * (ngrid + 1)]
            e_y.append(a)
        int_e_y = cumulative_trapezoid(x, e_y, initial=0)
        # periodic fields: subtract off DC component */
        # -- need this for consistency with charge conservation */
        # sum_ey = np.sum(int_e_y)
        # int_e_y -= sum_ey/ngrid
        int_e_y[0] = int_e_y[ngrid]
        E_y.append(int_e_y)
    E_y = np.array(E_y)
    E_y = np.transpose(E_y)
    electric_res = np.sqrt(np.multiply(E_x, E_x) + np.multiply(E_y, E_y))
    delta_E2 = np.multiply((electric_res - np.mean(electric_res)), (electric_res - np.mean(electric_res)))
    var_E = np.mean(delta_E2)

    return True


def magnetic_field(H_z):  # the points go from left to right and bottom to up
    global E_x, E_y, H_z_proj, variance_B
    for i in range(0, ngrid):  # x grid index
        for j in range(0, ngrid):  # y grid index
            H_z[i, j] = -dt * (((E_x[i + 1, j] - E_x[i, j]) / dx) - ((E_y[i, j + 1] - E_y[i, j]) / dx))

    # restructuring magnetic field for projection
    a83 = []
    a82 = []
    for i in range(0, ngrid):
        a8 = []
        a8.append(H_z[i][ngrid - 1])
        for j in range(0, ngrid):
            a8.append(H_z[i][j])
        a8.append(H_z[i][0])
        a82.append(a8)
    a83.append(a82[ngrid - 1])
    for i in range(0, ngrid):
        a83.append(a82[i])
    a83.append(a82[0])
    H_z_proj = np.array(a83)

    magnetic_res = np.sqrt(np.multiply(H_z, H_z))
    delta_B2 = np.multiply((magnetic_res - np.mean(magnetic_res)), (magnetic_res - np.mean(magnetic_res)))
    variance_B = np.mean(delta_B2)
    return True


def indexing():
    global pos_x, pos_y, index
    index = [[]for j in range(ngrid * ngrid)]
    a = np.floor(pos_x / dx)
    b = np.floor(pos_y / dx)
    for i in range(0, nparticles):
        j = a[i] + ngrid * b[i]
        j = int(j)
        index[j].append(i)
    return True


def push():
    global pos_x, pos_y, v_x, v_y, E_x, E_y, q_over_me, dt, dx, ngrid, H_z_proj
    for i in range(0, ngrid):  # x index
        for j in range(0, ngrid):  # y index
            a = index[i + ngrid * j]

            E_x1 = E_x[i, j]
            E_x2 = E_x[i, j + 1]
            E_x3 = E_x[i + 1, j]
            E_x4 = E_x[i + 1, j + 1]

            E_y1 = E_y[i, j]
            E_y2 = E_y[i, j + 1]
            E_y3 = E_y[i + 1, j]
            E_y4 = E_y[i + 1][j + 1]
            for k in range(len(a)):
                ab = a[k]
                a_1 = pos_x[ab]/dx
                a_2 = pos_y[ab]/dx

                index_x1 = int(a_1)
                index_y1 = int(a_2)
                weight_2x = a_1 - index_x1
                weight_1x = 1.0 - weight_2x
                weight_2y = a_2 - index_y1
                weight_1y = 1.0 - weight_2y

                Ex_1 = weight_1x * weight_1y * E_x1  # index[i][j]
                Ex_2 = weight_2x * weight_1y * E_x2  # index[i+1][j]
                Ex_3 = weight_1x * weight_2y * E_x3  # index[i][j+1]
                Ex_4 = weight_2x * weight_2y * E_x4  # index[i+1][j+1]
                Ex_r = Ex_1 + Ex_2 + Ex_3 + Ex_4  # resultant E_x

                Ey_1 = weight_1x * weight_1y * E_y1  # index[i][j]
                Ey_2 = weight_2x * weight_1y * E_y2  # index[i+1][j]
                Ey_3 = weight_1x * weight_2y * E_y3  # index[i][j+1]
                Ey_4 = weight_2x * weight_2y * E_y4  # index[i+1][j+1]
                Ey_r = Ey_1 + Ey_2 + Ey_3 + Ey_4  # resultant E_y

                # need to rotate the vector
                b_1 = index_x1 + 1  # index of the particle in the projected magnetic field array
                b_2 = index_y1 + 1

                # check the indexes
                h_1 = H_z_proj[b_2, b_1]
                if weight_2x > 0.5:
                    h_2 = H_z_proj[b_2][b_1 + 1]
                    if weight_2y > 0.5:
                        h_3 = H_z_proj[b_2 + 1][b_1]
                        h_4 = H_z_proj[b_2 + 1][b_1 + 1]
                    else:
                        h_3 = H_z_proj[b_2 - 1][b_1]
                        h_4 = H_z_proj[b_2 - 1][b_1 + 1]
                else:
                    h_2 = H_z_proj[b_2][b_1 - 1]
                    if weight_2y > 0.5:
                        h_3 = H_z_proj[b_2 + 1][b_1]
                        h_4 = H_z_proj[b_2 + 1][b_1 - 1]
                    else:
                        h_3 = H_z_proj[b_2 - 1][b_1]
                        h_4 = H_z_proj[b_2 - 1][b_1 - 1]
                # weight for magnetic field grid
                w_bx2 = abs(weight_2x - 0.5)    # 0.5 is subtracted due to shift in origin inside the grid
                w_bx1 = 1 - w_bx2
                w_by2 = abs(weight_2y - 0.5)
                w_by1 = 1 - w_by2

                Hz = (h_1 * w_bx1 * w_by1) + (h_2 * w_bx2 * w_by1) + (h_3 * w_bx1 * w_by2) + (h_4 * w_bx2 * w_by2)

                # Boris method
                qd = q_over_me * dt * 0.5
                h_z = qd * Hz
                sz = 2*h_z/(1 + h_z**2)

                ux = v_x[a[k]] + qd * Ex_r
                uy = v_y[a[k]] + qd * Ey_r

                uxd = ux + sz * (uy - h_z * ux)
                uyd = uy - sz * (ux + h_z * uy)

                v_x[a[k]] = uxd + qd * Ex_r
                v_y[a[k]] = uyd + qd * Ey_r

                pos_x[a[k]] += v_x[a[k]] * dt
                pos_y[a[k]] += v_y[a[k]] * dt


def energy():
    global E_x, E_y, H_z, v_x, v_y, field_energy, itime, particle_energy, total_energy

    # magnetic field energy
    magnetic_res_sqr = np.multiply(H_z, H_z)
    magnetic_energy = 0.5 * np.sum(magnetic_res_sqr) * dx ** 2

    # electric field energy
    electric_res_sqr = np.multiply(E_x, E_x) + np.multiply(E_y, E_y)
    a1 = electric_res_sqr[:-1, :-1]
    a2 = electric_res_sqr[:-1, 1:]
    a3 = electric_res_sqr[1:, :-1]
    a4 = electric_res_sqr[1:, 1:]
    electric_red_res = (a1 + a2 + a3 + a4)/4
    electric_energy = 0.5 * np.sum(electric_red_res) * dx**2

    # kinetic energy of the particles
    velocity_res_sqr = np.multiply(v_x, v_x) + np.multiply(v_y, v_y)
    kinetic_particle = 0.5 * mass * np.sum(velocity_res_sqr)

    field_energy[itime] = magnetic_energy + electric_energy
    particle_energy[itime] = kinetic_particle
    total_energy[itime] = field_energy[itime] + particle_energy[itime]
    return True


def charge_density_plot():
    global rho_t, itime, v_x, v_y
    x = np.linspace(0, 1, ngrid + 1)
    y = np.linspace(0, 1, ngrid + 1)
    rho_t2d = []
    for j in range(0, ngrid + 1):
        a = rho_t[j * (ngrid + 1):(j + 1) * (ngrid + 1)]
        rho_t2d.append(a)
    rho_t2d = np.array(rho_t2d)
    plt.subplot(1, 2, 1)
    plt.cla()
    z = rho_t2d
    plt.contourf(x, y, z, levels=100)
    plt.subplot(1, 2, 2)
    plt.cla()
    velocity_res_sqr = np.sqrt(np.multiply(v_x, v_x) + np.multiply(v_y, v_y))
    plt.hist(velocity_res_sqr, bins=50, density=True)
    plt.pause(0.0001)
    plt.draw()
    return True


def end_plot():
    t = np.arange(0, time_steps, 1)
    plt.clf()
    plt.subplot(2, 2, 1)
    plt.title('Convergence of Electric Field')
    plt.plot(t, electric_variance_array)
    plt.xlabel('Time steps')
    plt.ylabel('Variance')
    plt.xlim(0, time_steps)
    v = np.sqrt(np.multiply(v_x, v_x) + np.multiply(v_y, v_y))
    plt.subplot(2, 2, 2)
    plt.title('Velocity Distribution')
    plt.hist(v, bins=50, density=True)
    plt.xlabel('Velocity in arb. units')
    plt.ylabel('Normalised no. of particles')
    plt.xlim(0, 1.1*max(v))
    plt.subplot(2, 2, 3)
    plt.title('Convergence of Magnetic Field')
    plt.plot(t, magnetic_variance_array)
    plt.xlabel('Time steps')
    plt.ylabel('Variance')
    plt.xlim(0, time_steps)
    plt.subplot(2, 2, 4)
    plt.title('Energy Plot')
    plt.plot(t, total_energy, 'black', label='Total Energy')
    plt.plot(t, particle_energy, 'red', label='Kinetic Energy')
    plt.plot(t, field_energy, 'green', label='Field Energy')
    plt.legend()
    plt.xlim(0, time_steps)
    plt.ylim(0, max(total_energy) + 0.1 * max(total_energy))
    plt.xlabel('Time steps')
    plt.ylabel('Energy')
    plt.grid()
    plt.show()


# main program
# inputs
bc_particle = 1
ngrid = int(input('enter the value of grid: '))
nparticles = int(input('enter the no. of particles(a perfect square): '))  # always enter a perfect square for now
two_stream = int(input('enter 1 for streaming else 0: '))
v_x = np.zeros(nparticles)  # velocity array
v_y = np.zeros(nparticles)
length = 1
x = np.linspace(0, 1, ngrid + 1)
dx = np.diff(x)[0]  # grid spacing
dt = 0.005  # time step
H_z = np.array([[0] * ngrid] * ngrid, dtype=float)  # initial magnetic field array
q_over_me = -1.0
# this is from the downloaded one
charge = -1 * dx * dx
mass = charge / q_over_me
time_steps = 1500
field_energy = np.zeros(time_steps)
particle_energy = np.zeros(time_steps)
total_energy = np.zeros(time_steps)
electric_variance_array = []
magnetic_variance_array = []
density_array = []
# main program
x_load(nparticles)
for i in range(0, time_steps):
    print(i)
    itime = i
    projection()
    electric_field()
    magnetic_field(H_z)
    density_array.append(0.25*(rho_t[5] + rho_t[6] + rho_t[5 + (ngrid+1)] + rho_t[6 + (ngrid + 1)]))
    electric_variance_array.append(var_E)
    magnetic_variance_array.append(variance_B)
    energy()
    indexing()
    push()
    boundary_condition(bc_particle)
print('Done')
x = np.arange(1200, 1250, 1)
print(x)
print(density_array)
plt.subplot(1, 2, 1)
plt.scatter(x, density_array[1200:1250])
inter_func = sp.interp1d(x, density_array[1200:1250], 'cubic')
plt.plot(x, inter_func(x))
plt.subplot(1, 2, 2)
v = np.multiply(v_x, v_x) + np.multiply(v_y, v_y)
plt.hist(v, bins=50, density=True)
plt.xlabel('Velocity squared in arb. units')
plt.ylabel('Normalised no. of particles')
plt.xlim(0, 1.1*max(v))
plt.show()

