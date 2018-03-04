""" Functions for pre-atmosphere velocity corrections. """

# Make this scripts both Python 2 and 3 compatible
from __future__ import print_function, division, absolute_import


import math



def loadFitCSV(file_name, delimiter=';'):
    """ Loads velocity difference fit data. """


    with open(file_name) as f:

        # Skip the header
        next(f)


        data = []

        # Read velocity, zenith angle and fit parameters
        for line in f:

            line = line.replace('\n', '').replace('\r', '')
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

    return a + b*zangle + c*math.exp(d*zangle + e) + f*math.exp(g*zangle**2 + e)



def velocityCorrection(v_init, zangle, meteoroid_type, system_type):
    """ Returns a difference in velocity for the given meteoroid type, observation system, initial 
        velocity and zenith angle, as given by Vida et al. 2017. For the areas of the velocity/zenith angle 
        phase space where no simulations were above the detection limit, the difference is taken for the
        closest available velocity.


    Arguments:
        v_init: [float] Initial velocity (km/s).
        zangle: [float] Zenith angle (degrees).
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

    # Define CSV file names with velocity fits
    intensified_csvs = ['sim_intensified_cometary_fits.csv', 'sim_intensified_asteroidal_fits.csv', \
        'sim_intensified_iron_fits.csv']
    moderate_csvs = ['sim_moderate_cometary_fits.csv', 'sim_moderate_asteroidal_fits.csv', \
        'sim_moderate_iron_fits.csv']
    allsky_csvs = ['sim_allsky_cometary_fits.csv', 'sim_allsky_asteroidal_fits.csv', \
        'sim_allsky_iron_fits.csv']
    

    # Choose the appropriate CSV file to load
    if system_type == 'intensified':
        csv_list = intensified_csvs

    elif system_type == 'moderate':
        csv_list = moderate_csvs

    elif system_type == 'allsky':
        csv_list = allsky_csvs

    else:
        raise ValueError("system_type = " + system_type + " not found! Try using 'intensified', 'moderate' or 'allsky'.")


    # Choose the appropriate meteoroid type
    if meteoroid_type == 'cometary':
        csv_file = csv_list[0]

    elif meteoroid_type == 'asteroidal':
        csv_file = csv_list[1]

    elif meteoroid_type == 'iron-rich':
        csv_file = csv_list[2]

    else:
        raise ValueError("meteoroid_type = " + meteoroid_type + " not found! Try using 'comeraty', 'asteroidal' or 'iron-rich'.")

    
    # Load the appropriate CSV file
    fit_data = loadFitCSV(csv_file)
    
    # Take only those fits for which the minimum zenith angle is lower than the given zenith angle
    fit_data = [line for line in fit_data if line[1] <= math.radians(zangle)]

    # Find the closest fitted velocity to the given initial velocity
    vel_temp = [abs(line[0]/1000 - v_init) for line in fit_data]
    vel_indx = vel_temp.index(min(vel_temp))

    # Take the appropriate fit parameters
    fit_params = fit_data[vel_indx][2:]

    # Calculate the velocity difference in km/s
    return zangleModel(math.radians(zangle), *fit_params)/1000




if __name__ == "__main__":

    
    # INITIAL VELOCITY (km/s)
    v_init = 20.0

    # ZENITH ANGLE (deg)
    zangle = 45.0


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
    delta_v = velocityCorrection(v_init, zangle, meteoroid_type, system_type)

    # Print velocity correction in km/s
    print("Correction for {:s} meteoroids observed by {:s} systems with velocity of {:.2f} km/s: {:.3f} km/s.".format(meteoroid_type,
        system_type, v_init, delta_v))