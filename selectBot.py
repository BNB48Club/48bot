


def selectBot(accounts):
    print("Which bot do you want to proceed with:")
    for account in accounts:
        print("[{}]".format(account))
    name = "somethingdefinitelynotexist"
    while not name in accounts:
        print(">",end="")
        name = input()
    return accounts[name];
