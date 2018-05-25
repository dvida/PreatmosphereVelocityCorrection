""" Functions for pre-atmosphere velocity corrections. """

# Make this scripts both Python 2 and 3 compatible
from __future__ import print_function, division, absolute_import


import math



def loadFitCSV(file_name, delimiter=';'):
    """ Loads velocity difference fit data. """


    with open(file_name) as f:

        data = []

        # Read velocity, zenith angle and fit parameters
        for line in f:

            # Remove newline characters
            line = line.replace('\n', '').replace('\r', '')

            # Skip the header
            if line[0] == '#':
                continue

            # Add data to list
            line = list(map(float, line.split(delimiter)))

            data.append(line)


        return data



def zangleModel(zangle, a, b, c, d, e, f, g):
    """ Given the zenith angle and fit parameters, return the veloicty difference for the given value of
        initial velocity.
    
    Arguments:
        zangle: [float] Zenith angle (radians).
        a, b, c, d, e, f, g: [float] Fit parameters.

    Return:
        [float] Velocity difference in m/s
    """

    return a + b*zangle + c*zangle**2 + d*zangle**3 + e*zangle**4 + f*zangle**5 + g*zangle**6




def velocityCorrection(v_init, peak_mag, zangle, meteoroid_type, system_type):
    """ Returns a difference in velocity for the given meteoroid type, observation system, initial 
        velocity and zenith angle, as given by Vida et al. 2017. For the areas of the velocity/zenith angle 
        phase space where no simulations were above the detection limit, the difference is taken for the
        closest available velocity.


    Arguments:
        v_init: [float] Initial velocity (km/s).
        peak_mag: [float] Peak magnitude of the meteor.
        zangle: [float] Zenith angle (degrees). If larger than 75 deg, it will be limited to 75 deg, as larger
            values were not simulated.
        meteoroid_type: [str] Type of meteoroid.
            - 'cometary' - density 360 to 1510 kg/m^3, ablation coeficient 0.1 s^2/km^2 
            - 'asteroidal' - density 2500 to 3500 kg/m^3, ablation coeficient 0.042 s^2/km^2 
            - 'iron-rich'- density 4150 to 5425 kg/m^3, ablation coeficient 0.07 s^2/km^2 
        system_type: [str] Type of observational system.
            - 'intensified' - Image intensified system with LM = +6.5. WMPG influx system, CAMO.
            - 'moderate' - Moderate FOV system with LM = +5.0. CAMS, SonotaCo, IMO network.
            - 'allsky' - All-sky fireball system with LM = -0.5. ASGARD, EN, DFN.
    

    Return:
        [float] Velocity difference in km/s.
    """


    # Limit the zenith angle to 75 degrees
    if zangle > 75:
        zangle = 75.0


    # Define CSV file name with fits
    preatm_csv_name = 'preatmosphere_fits.csv'
    

    # Choose the appropriate system id
    if system_type == 'intensified':
        system_id = 2

    elif system_type == 'moderate':
        system_id = 1

    elif system_type == 'allsky':
        system_id = 0

    else:
        raise ValueError("system_type = " + system_type + " not found! Try using 'intensified', 'moderate' or 'allsky'.")


    # Choose the appropriate meteoroid id
    if meteoroid_type == 'cometary':
        meteoroid_id = 0

    elif meteoroid_type == 'asteroidal':
        meteoroid_id = 1

    elif meteoroid_type == 'iron-rich':
        meteoroid_id = 2

    else:
        raise ValueError("meteoroid_type = " + meteoroid_type + " not found! Try using 'comeraty', 'asteroidal' or 'iron-rich'.")

    
    # Load the appropriate CSV file
    fit_data = loadFitCSV(preatm_csv_name)

    # Take only those fits which correspond to the given system and meteoroid type
    fit_data = [line for line in fit_data if line[0] == system_id]
    fit_data = [line for line in fit_data if line[1] == meteoroid_id]

    # Compute absolute differences between the given velocity and velocities in the table
    vel_diffs = [abs(line[2]/1000 - v_init) for line in fit_data]

    # Find indices with best matching velocities
    vel_indices = [i for i, x in enumerate(vel_diffs) if x == min(vel_diffs)]
    
    # Compute absolute differences between the given magnitude and magnitudes of the given velocity
    mag_diffs = [abs(fit_data[vel_ind][3] - peak_mag) for vel_ind in vel_indices]

    # Find the best matching magnitude for the given velocity
    mag_ind = mag_diffs.index(min(mag_diffs))

    print('Matched table entry:')
    print(fit_data[vel_indices[mag_ind]])
    print()

    # Take the appropriate fit parameters
    fit_params = fit_data[vel_indices[mag_ind]][4:]

    # Computethe velocity difference in km/s
    return zangleModel(math.radians(zangle), *fit_params)/1000




if __name__ == "__main__":

    
    # INITIAL VELOCITY (km/s)
    v_init = 20.0

    # ZENITH ANGLE (deg)
    zangle = 45.0

    # Peak magnitude
    peak_mag = 2.0


    ### SET METEOROID TYPE
    # meteoroid_type: [str] Type of meteoroid.
    #   - 'cometary' - density 180 to 1510 kg/m^3, ablation coeficient 0.1 s^2/km^2 
    #   - 'asteroidal' - density 2000 to 3500 kg/m^3, ablation coeficient 0.042 s^2/km^2 
    #   - 'iron-rich'- density 4150 to 5425 kg/m^3, ablation coeficient 0.07 s^2/km^2 
    meteoroid_type = 'cometary'

    ### SET SYSTEM TYPE
    # system_type: [str] Type of observational system.
    #     - 'intensified' - Image intensified system with LM = +7.5. WMPG influx system, CAMO.
    #     - 'moderate' - Moderate FOV system with LM = +5.0. CAMS, SonotaCo, IMO network.
    #     - 'allsky' - All-sky fireball system with LM = -0.5. ASGARD, EN, DFN.
    system_type = 'moderate'

    # Calculate velocity correction
    delta_v = velocityCorrection(v_init, peak_mag, zangle, meteoroid_type, system_type)

    # Print velocity correction in km/s
    print("Correction for {:s} meteoroids observed by {:s} systems with velocity of {:.2f} km/s, peak magnitude {:+.2f} and zenith angle of {:.2f}: {:.3f} km/s.".format(meteoroid_type,
        system_type, v_init, peak_mag, zangle, delta_v))