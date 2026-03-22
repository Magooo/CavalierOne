try:
    with open("model_log.txt", "r") as f:
        print(f.read())
except Exception as e:
    print(e)
