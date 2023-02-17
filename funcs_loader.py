def add_functionality(bot, **kwargs):
    print("==========================================================================================")
    print("Adding functionality to bot\n")
    func_classes = {}
    logger = None
    if 'logger' in kwargs:
        print("adding logger functionality")
        logger = kwargs['logger'](bot)
        func_classes['logger'] = logger
        kwargs.pop('logger')
        print('\n')

    for key, value in kwargs.items():
        print(f"adding {key} functionality")
        func_classes[key] = value(bot)
        print('\n')
    print("==========================================================================================")
    return func_classes