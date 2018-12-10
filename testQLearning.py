from QLearning import QLearningAgent
import utils

def main():
    env = utils.setupEnv('MarLo-FindTheGoal-v0')
    # Get the number of available actions, minus waiting action
    actionSize = env.action_space.n

    epsilonDecay = 0.97
    alphas = [0.5, 0.1, 0.8]
    gammas = [1, 0.5]
    runs = [1,2,3]

    #alphas = [0.1, 0.8,  0.01]
    #gammas = [1,0.5]

    for i in runs:
        for alpha in alphas:
            for gamma in gammas:
                QTableName = str(i) + "_QTable_Alpha_" + str(alpha).replace(".", "_") + "_Gamma_" + str(gamma).replace(".","_") + "_Decay_" + str(epsilonDecay).replace(".", "_") + ".json"
                CSVName = str(i) + "_Test_Results_Alpha_" + str(alpha).replace(".", "_") + "_Gamma_" + str(gamma).replace(".", "_")+ "_Decay_" + str(epsilonDecay).replace(".", "_") + ".csv"

                myAgent = QLearningAgent(actionSize, 20, QTableName,CSVName, True, epsilonDecay , alpha, gamma,0.00,training = True)

                print("\n\n -------------- Starting test run of Decay %s, Alpha %s and Gamma %s --------- \n \n" % (epsilonDecay,alpha,gamma))

                # Start the running of the Agent
                myAgent.runAgent(env)

    return

if __name__ == "__main__":
    main()