def calculate_percentage(now_exp):
    accumulate = (
        # 10, 9590, 23030, 42110, 69590,  # bronze
        # 109430, 182155, 289055, 447280, 683030,  # silver
        # 1036655, 1675295, 2639645, 4100615, 6321305,  # gold
        # 10866705, 16048125, 24001635, 36250035, 55173795,  # platinum
        # 84505965, 130116585, 201274515, 312629175, 487455975,  # diamond
        # 854592255, 1434667575, 2354086975, 3815963815, 6147157375  # ruby

        10, 9600, 23040, 42120, 69600,  # bronze
        109440, 182165, 289065, 447290, 683040,  # silver
        1036665, 1675305, 2639655, 4100625, 6321315,  # gold
        10836715, 16018135, 23971645, 36220045, 55143805,  # platiunm
        84475615, 130086595, 201244525, 312599185, 487425985,  # diamond
        854562265, 1434637585, 2354056985, 3815933825, 6147627385  # ruby
    )

    i = 0
    try:
        for exp in accumulate:  # 루비 1 예외처리하기
            if now_exp - exp < 0:
                temp = now_exp - accumulate[i - 1]
                break
            i += 1
        need_exp = accumulate[i] - accumulate[i - 1]
        now_percentage = int(temp / need_exp * 100)

        return now_percentage
    except:
        return 100
