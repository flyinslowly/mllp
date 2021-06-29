# MLLP: MachineLearning-LoanPricing

MLLP - это исследовательский проект, оптимизирующий затраты процесса расчёта справедливой стоимости банковского кредита с помощью существующего калькулятора кредитов LoanPricer. 

Фреймворк написан на языке Python 3.6.

В данный момент осуществлена поддержка обучения собственных моделей гауссовского процесса для моделирования неизвестного распределения справедливых стоимостей кредитов в зависимости от рыночных данных.

## Использование

Для удобной работы с обучающими примерами реализованы следующие классы:
- DataBuilder - неактуален. Создает датафрейм признаков NxK.
- FeatureTransformer - неактуален. Трансформирует сделку в признаковое пространство фиксированной размерности.
- HistMarketDataWorker - калибрует параметры нормального распределения исторической маркетдаты, умеет сохранять и загружать это распределенеие.
- LoanConcatenator - конкатенирует структуру опции и маркетдату кредита во внутренних форматах. Умеет сохранить такой кредит в JSON. Можно не передавать маркетдату для сделок с fixed расписанием платежей.
- LoanMarkuper - отправляет JSON кредита на сервер LoanPricer для получения его справедливой стоимости.
- LoanOptionsMaker - класс, пользующийся HistMarketDataWorker. По сути просто семплирует кривую дисконтфакторов для бездефолтного клиента. Результат - опции во внутреннем формате.
- LoanStructGenerator - неактуален. запускает генерацию структуры сделки.
- LoanStructReader - читает структуру сделки, переданной в формате JSON во внутренний формат.

Пример чтения с калибровкой исторического распределения, семплирования кривой и сохранения функции распределения:

    hmdw = HistMarketDataWorker(DEFAULT_CURVES_PATH, DEFAULT_CURVE_NAME).load()
    hmdw.get_sample()
    hmdw.save()

Пример чтения структуры сделки из JSON во внутренний формат:

    from feature_extraction.loan_struct_reader import LoanStructReader
    json_example_path = os.path.join(PROJECT_PATH, r"json_real", r"sample_1.json")
    struct, original_options = LoanStructReader().Read(json_example_path, returnOptions=True)
    
Пример аугментирования кривой дисконтфакторов irCurve:
    
    from feature_extraction.loan_options_maker import LoanOptionsMaker
    options = LoanOptionsMaker().Make(original_options)
    print(options['irOptions_curve']['values'])
    
Пример конкатенирования внутренних представлений и сохранения сделки в JSON:
  
    from feature_extraction.loan_concatenator import LoanConcatenator
    js = LoanConcatenator(struct, options, {}).Parse()
    LoanConcatenator.Save(js, os.path.join(PROJECT_PATH, r"json_augmented", r"sample.json"))
    
Пример прайсинга сделки в формате JSON через LoanPricer:    
    
    from feature_extraction.loan_markuper import LoanMarkuper
    markuper = LoanMarkuper()
    loan = LoanConcatenator(struct, options, {}).Parse()
    markuper.MarkupLoan(loan)

## Лицензия
© Sber 2021.