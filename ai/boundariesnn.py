import numpy as np

class BoundariesNN:
    """
    Class for predicting the northern and southern boundaries of the QG model using a neural net.
    """

    # Name of output files (minus extension)
    out_file = "boundariesnn"

    # Number of hidden layers and nodes per hidden layer
    n_hidden_layers = 2
    n_per_hidden_layer = 40

    # Number of input and output variables to neural net
    # Stencil size * number of layers * number of variables
    n_input = 6*2*3
    # Number of layers * number of variables
    n_output = 2*3

    def __init__(self):
        from numerical_model.qg_constants import qg_constants as const
        from util import build_model

        # Build model for inference
        self.model = build_model(
            BoundariesNN.n_input, BoundariesNN.n_output,
            BoundariesNN.n_hidden_layers, BoundariesNN.n_per_hidden_layer
        )

        # Try loading weights file
        try:
            self.model.load_weights(f"{BoundariesNN.out_file}.hdf", by_name=False)
        except OSError as e:
            print("Weights file for BoundariesNN doesn't exist\nHave you trained this model yet?")
            raise e

        # Store number of longitudes
        self.n_lon = int(const.nx)

    """
    Compute tendencies of the variables on the northern and southern boundaries.
    """
    def get_tend(self, q, u, v):
        # Prepare input array for neural net
        infer_in = np.zeros((self.n_lon*2,6*2*3))

        # Loop over all longitudes, extracting the northern and southern boundary variables
        i = 0
        for x in range(self.n_lon):
            infer_in[i,:6*2]     = BoundariesNN.get_stencil(q, x, self.n_lon)
            infer_in[i,6*2:12*2] = BoundariesNN.get_stencil(u, x, self.n_lon)
            infer_in[i,12*2:]    = BoundariesNN.get_stencil(v, x, self.n_lon)
            i+=1

            infer_in[i,:6*2]     = BoundariesNN.get_stencil(q[:,::-1,:], x, self.n_lon)
            infer_in[i,6*2:12*2] = BoundariesNN.get_stencil(u[:,::-1,:], x, self.n_lon)
            infer_in[i,12*2:]    = BoundariesNN.get_stencil(v[:,::-1,:], x, self.n_lon)
            i+=1

        # Normalize input
        infer_in = BoundariesNN.normalize(infer_in)

        # Predict new tendencies (tendencies include dt term)
        tendencies = self.model.predict(infer_in, batch_size=1)

        # Unpack tendencies
        q_tend = np.zeros((self.n_lon,2,2))
        u_tend = np.zeros((self.n_lon,2,2))
        v_tend = np.zeros((self.n_lon,2,2))
        q_tend[:,:,0] = tendencies[:,0].reshape((self.n_lon,2))
        q_tend[:,:,1] = tendencies[:,1].reshape((self.n_lon,2))
        u_tend[:,:,0] = tendencies[:,2].reshape((self.n_lon,2))
        u_tend[:,:,1] = tendencies[:,3].reshape((self.n_lon,2))
        v_tend[:,:,0] = tendencies[:,4].reshape((self.n_lon,2))
        v_tend[:,:,1] = tendencies[:,5].reshape((self.n_lon,2))
        # q_tend = tendencies[:,:2].reshape((self.n_lon,2,2))
        # u_tend = tendencies[:,2:4].reshape((self.n_lon,2,2))
        # v_tend = tendencies[:,4:].reshape((self.n_lon,2,2))

        return q_tend, u_tend, v_tend

    """
    Train the neural net based on the input training data of q (quasigeostrophic vorticity), u
    (zonal wind) and v (meridional wind).
    """
    @staticmethod
    def train(q, u, v):
        from util import build_model, save_history

        # Get dimensions
        n_lon, n_lat, _, n_time = q.shape
        print(f"{n_lon} longitudes, {n_lat} latitudes, 2 levels, {n_time} timesteps")

        # Compute number of training pairs
        # 2 (top and bottom) * number of time steps (minus 1) * number of layers
        # * number of longitudes
        n_train = 2*(n_time-1)*2*n_lon

        print(f"Training with {n_train} training pairs,\
            dimensions: ({BoundariesNN.n_input}, {BoundariesNN.n_output})")

        # Define input and output arrays
        train_in  = np.zeros((n_train,BoundariesNN.n_input))
        train_out = np.zeros((n_train,BoundariesNN.n_output))

        # Prepare training data. Different grid points and time steps are considered as independent
        # training pairs. The northern and southern boundaries are also treated equivalently, only
        # the southern boundary is flipped
        i = 0
        for t in range(n_time-1):
            for x in range(n_lon):
                # Form training pairs for top of domain
                train_in[i,:6*2]     = BoundariesNN.get_stencil(q[...,t], x, n_lon)
                train_in[i,6*2:12*2] = BoundariesNN.get_stencil(u[...,t], x, n_lon)
                train_in[i,12*2:]    = BoundariesNN.get_stencil(v[...,t], x, n_lon)
                train_out[i,:2]  = q[x,0,:,t+1] - q[x,0,:,t]
                train_out[i,2:4] = u[x,0,:,t+1] - u[x,0,:,t]
                train_out[i,4:]  = v[x,0,:,t+1] - v[x,0,:,t]
                i+=1

                # Form training pairs for bottom of domain (just reverse the vertical coordinate
                # and call the same function)
                train_in[i,:6*2]     = BoundariesNN.get_stencil(q[:,::-1,:,t], x, n_lon)
                train_in[i,6*2:12*2] = BoundariesNN.get_stencil(u[:,::-1,:,t], x, n_lon)
                train_in[i,12*2:]    = BoundariesNN.get_stencil(v[:,::-1,:,t], x, n_lon)
                train_out[i,:2]  = q[x,-1,:,t+1] - q[x,-1,:,t]
                train_out[i,2:4] = u[x,-1,:,t+1] - u[x,-1,:,t]
                train_out[i,4:]  = v[x,-1,:,t+1] - v[x,-1,:,t]
                i+=1

        # Normalize input
        train_in = BoundariesNN.normalize(train_in)

        print("Training data prepared")

        # Build model for training
        model = build_model(
            BoundariesNN.n_input, BoundariesNN.n_output,
            BoundariesNN.n_hidden_layers, BoundariesNN.n_per_hidden_layer
        )

        # Train!
        history = model.fit(train_in, train_out, epochs=200, batch_size=128, validation_split=0.2)

        # Output weights and diagnostics files
        save_history(f"{BoundariesNN.out_file}_history.txt", history)
        model.save_weights(f"{BoundariesNN.out_file}.hdf")

    """
    Extracts the stencil corresponding to the requested longitude.
    e.g. if you request the 2nd longitude (index starting from 0)
    ---------------------------    -------
    |a|b|c|d|e|f|g|h|i|j|k|l|m|    |b|c|d|
    --------------------------- => -------
    |n|o|p|q|r|s|t|u|v|w|x|y|z|    |o|p|q|
    ---------------------------    -------
    """
    @staticmethod
    def get_stencil(full_array, lon, n_lon):
        top = full_array[:,:2,:]
        stencil = top[np.array(range(lon-1,lon+2))%n_lon,:,:]
        return stencil.flatten()

    """
    Normalize the given training data so values are between -1.0 and 1.0.
    """
    @staticmethod
    def normalize(training_data):
        # Maximum and minimum values of q, u, and v based on a long run of the numerical model
        q_max, q_min = 40.0, -37.0
        u_max, u_min = 10.0, -6.0
        v_max, v_min = 2.0, -2.0

        # Normalize the training data
        normalized = training_data[:,:]
        normalized[:,:6*2]     = 2.0*(normalized[:,:6*2]     - q_min)/(q_max - q_min) - 1.0
        normalized[:,6*2:12*2] = 2.0*(normalized[:,6*2:12*2] - u_min)/(u_max - u_min) - 1.0
        normalized[:,12*2:]    = 2.0*(normalized[:,12*2:]    - v_min)/(v_max - v_min) - 1.0
        return normalized