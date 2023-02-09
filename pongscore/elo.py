# ELO K-factor
def elo_K(loser_score):
    if loser_score < 2:
        return 60
    elif loser_score < 5:
        return 40
    elif loser_score < 8:
        return 30
    elif loser_score < 11:
        return 25
    else:
        return 20


def calc_elo(R1, R2, winner, ls):
    '''
    winner = 1 if R1 wins else 0
    SOURCE: https://metinmediamath.wordpress.com/2013/11/27/how-to-calculate-the-elo-rating-including-example/
    '''
    K = elo_K(ls)
    
    # Transformed score
    R1T = pow(10, R1/400)
    R2T = pow(10, R2/400)

    # Expected score
    E1 = R1T / (R1T + R2T)
    E2 = R2T / (R1T + R2T)

    # Score
    S1 = 1 if winner == 1 else 0
    S2 = abs(S1 - 1)

    # Updated elo
    ELO1 = R1 + K * (S1 - E1)
    ELO2 = R2 + K * (S2 - E2)

    return ELO1, ELO2


if __name__ == "__main__":
    print(calc_elo(1500, 1500, 1, 9))