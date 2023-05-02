from hyperas import optim
from model_prototype import *
from hyperopt import Trials, tpe

if __name__ ==  '__main__': 
    best_run, best_model = optim.minimize(model=model, 
				       					  data=data, 
										  algo=tpe.suggest, 
										  max_evals=10, 
										  trials=Trials())
    best_model.save("model.h5")