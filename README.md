# boenbot
VK picture bot

# Обзор
Бот для группы в ВК, в беседе или в лс отслеживает дубликаты присланных изображений, при детектировании - отправляет предполагаемый дубликат с тегом отправившего.

## Функционал и использемые технологии
### Основная функция - конвертирование и сравнение изображений. 
При получении временно сохраняет изображение во втором минимальном разрешении в папку диалога, сохраняя при этом название файла в txt-логе. 
Далее с помощью OpenCV происходит ресайз и перевод изображения в оттенки серого, после чего файл сохраняется как сжатый np.ndarray. 
Подготовленное изображение сравнивается с последними 2000 изображениями (хранимый максимум), присланными в данный диалог, в четыре потока (по 500 файлов в каждом). 
В процессе сравнения используется проверка индекса структурного сходства (SSIM) между полученным и имеющимися изображениями с помощью модуля skimage с последующей оценкой схожести (в отношении).
При схожести более 95% полученное изображение считается дублиактом (параметр настраиваемый).

### Рандомный арт
По команде производит парсинг и отправляет изображение, сгенерированное нейросетью на стороннем сайте. Результат зачастую пугающий.

### Поиск источника
По команде использует selenium и geckodriver для открытия браузера Firefox и поиска изображения через Яндекс.Картинки. В зависимости от успеха может отправить сообщение в нескольких вариантах:
1. Ссылка на твиттер + первая ссылка поиска.
2. Рандомное изображение из вкладки "похожие" + первая ссылка поиска.