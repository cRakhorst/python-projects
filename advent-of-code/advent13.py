ClawList = []
LineList = []
with open("day13.txt", "r") as data:
    for t in data:
        Line = t.strip()
        if Line.startswith("Button"):
            X, Y = Line.split(", Y+")
            _, X = X.split("+")
            X, Y = int(X), int(Y)
            LineList.append(X)
            LineList.append(Y)
        elif Line.startswith("Prize"):
            X, Y = Line.split(", Y=")
            _, X = X.split("=")
            X, Y = int(X), int(Y)
            LineList.append(X)
            LineList.append(Y)
        else:
            ClawList.append(tuple(LineList))
            LineList = []

ClawList.append(tuple(LineList))

def Claw(AX, AY, BX, BY, TX, TY):
    LowestCoins = 2**40
    Found = False
    MaxA = TX//AX
    for NA in range(MaxA+2):
        if NA*3 >= LowestCoins:
            return LowestCoins
        NewTargetX, NewTargetY = TX - NA*AX, TY - NA*AY
        if (NewTargetX < 0 or NewTargetY < 0) and not(Found):
            return 0
        elif (NewTargetX < 0 or NewTargetY < 0) and Found:
            return LowestCoins
        if NewTargetX % BX != 0 or NewTargetY % BY != 0:
            continue
        BCountX, BCountY = NewTargetX//BX, NewTargetY//BY
        if BCountX == BCountY:
            NewCoin = 3*NA + BCountX
            LowestCoins = min(NewCoin, LowestCoins)
            Found = True

        
def Claw2(AX, AY, BX, BY, TX, TY):
    TX += 10000000000000
    TY += 10000000000000
    if (AY*TX-AX*TY) % (AY*BX-AX*BY) == 0:
        BPresses = (AY*TX-AX*TY)//(AY*BX-AX*BY)
        if (TX - BX*BPresses) % AX == 0:
            APresses = (TX - BX*BPresses)//AX
            #print(BPresses, APresses)
            return 3*APresses+BPresses
    return 0


Part1Answer = 0
Part2Answer = 0
for AX, AY, BX, BY, TX, TY in ClawList:
    Part1Answer += Claw(AX, AY, BX, BY, TX, TY)
    Part2Answer += Claw2(AX, AY, BX, BY, TX, TY)

print(f"{Part1Answer = }")
print(f"{Part2Answer = }")