from flask import Flask, render_template, request
import sqlite3

city_map = {
    'bialystok': 'Białystok',
    'bydgoszcz': 'Bydgoszcz',
    'czestochowa': 'Częstochowa',
    'gdansk': 'Gdańsk',
    'gdynia': 'Gdynia',
    'katowice': 'Katowice',
    'krakow': 'Kraków',
    'lodz': 'Łódź',
    'lublin': 'Lublin',
    'poznan': 'Poznań',
    'radom': 'Radom',
    'rzeszow': 'Rzeszów',
    'szczecin': 'Szczecin',
    'warszawa': 'Warszawa',
    'wroclaw': 'Wrocław'
}

cities = sorted(city_map.keys())


app = Flask(__name__)

# funkcja do pobierania danych z bazy z filtrami
def get_filtered_apartments(city=None, min_rooms=None, min_square=None, max_square=None,
                            min_price=None, max_price=None, kindergarten=None, school=None,
                            balcony=None, elevator=None, parking=None, min_floor=None,
                            max_floor_count=None, sort_by=None):
    
    connection = sqlite3.connect('apartments_sale.db')

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    query = 'SELECT * FROM apartments WHERE 1=1'
    params = []

    if city:
        query += ' AND city LIKE ?'
        params.append(f'%{city.lower()}%')

    # FILTRY LICZBOWE

    if min_rooms is not None:
        query += ' AND rooms >= ?'
        params.append(min_rooms)

    if min_square is not None:
        query += ' AND squareMeters >= ?'
        params.append(min_square)

    if max_square is not None:
        query += ' AND squareMeters <= ?'
        params.append(max_square)

    if min_price is not None:
        query += ' AND price >= ?'
        params.append(min_price)

    if max_price is not None:
        query += ' AND price <= ?'
        params.append(max_price)

    if min_floor is not None:
        query += ' AND floor >= ?'
        params.append(min_floor)

    if max_floor_count is not None:
        query += ' AND floorCount <= ?'
        params.append(max_floor_count)

    # FILTRY TEKSTOWE
    if kindergarten == 'yes':
        query += ' AND kindergartenDistance <= 1'

    if school == 'yes':
        query += ' AND schoolDistance <= 1'

    if balcony == 'yes':
        query += ' AND hasBalcony = "yes"'

    if elevator == 'yes':
        query += ' AND hasElevator = "yes"'

    if parking == 'yes':
        query += ' AND hasParkingSpace = "yes"'
    
    # sortowanie rosnąco
    valid_sort_columns = ['rooms', 'squareMeters', 'floor', 'floorCount', 'price', 'kindergartenDistance', 'schoolDistance', 'city']
    if sort_by in valid_sort_columns:
        query += f' ORDER BY {sort_by} ASC'

    query += ' LIMIT 25' # wynik ograniczony do 25 rekordów

    cursor.execute(query, params)
    results = cursor.fetchall()
    connection.close()
    return results


# Strona główna
@app.route('/', methods=['GET', 'POST'])
def index():
    # pobiera wartości nawet jeśli puste
    filters = {
        'city': request.form.get('city', ''),
        'min_rooms': request.form.get('min_rooms', ''),
        'min_square': request.form.get('min_square', ''),
        'max_square': request.form.get('max_square', ''),
        'min_price': request.form.get('min_price', ''),
        'max_price': request.form.get('max_price', ''),
        'kindergarten': request.form.get('kindergarten', ''),
        'school': request.form.get('school', ''),
        'balcony': request.form.get('balcony', ''),
        'elevator': request.form.get('elevator', ''),
        'parking': request.form.get('parking', ''),
        'min_floor': request.form.get('min_floor', ''),
        'max_floor_count': request.form.get('max_floor_count', '')
    }

    # parametr sortowania z GET
    sort_by = request.form.get('sort_by', '')

    # konwersja wartości liczbowych
    int_keys = ['min_rooms', 'min_floor', 'max_floor_count']
    float_keys = ['min_square', 'max_square', 'min_price', 'max_price']

    for key in int_keys:
        if filters[key] != '':
            filters[key] = int(filters[key])
        else:
            filters[key] = None

    for key in float_keys:
        if filters[key] != '':
            filters[key] = float(filters[key])
        else:
            filters[key] = None
    
    results = get_filtered_apartments(**filters, sort_by=sort_by) if request.method == 'POST' else []

    return render_template(
        'index.html',
        results=results,
        filters=filters,
        cities=cities,
        city_map=city_map,
        sort_by=sort_by  # <-- przekazujemy osobno
    )



if __name__ == '__main__':
    app.run(debug=True)

