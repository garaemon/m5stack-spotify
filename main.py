from m5stack import lcd
import uos
import urequests
import ujson
import utime
import gc

from wifilib import connect_wifi

g_track_id = None
g_track_img = None
g_spotify_token = None
g_showing_spotify_logo = False


def read_json(filename):
    'read json from specified filename'
    try:
        lcd.println('reading {}'.format(filename))
        with open(filename, 'r') as f:
            return ujson.load(f)
    except:
        lcd.println('Error in reading json: ' + str(e))


private_json = read_json('private.json')
SPOTIFY_CLIENT_ID = private_json['SPOTIFY_CLIENT_ID']
SPOTIFY_CLIENT_SECRET = private_json['SPOTIFY_CLIENT_SECRET']
BASE64_SPOTIFY_CLIENT_ID_SECRET = private_json[
    'BASE64_SPOTIFY_CLIENT_ID_SECRET']
REDIRECT_URI = private_json['REDIRECT_URI']
SPOTIFY_ACESS_TOKEN = private_json['SPOTIFY_ACESS_TOKEN']
SPOTIFY_REFRESH_TOKEN = private_json['SPOTIFY_REFRESH_TOKEN']
WIFI_CONFIG = private_json['WIFI_CONFIG']

SPOTIFY_API_CURRENTLY_PLAYING_URL = 'https://api.spotify.com/v1/me/player/currently-playing'
SPOTIFY_API_REFRESH_URL = 'https://accounts.spotify.com/api/token'


def write_file(output_file, content):
    with open(output_file, 'wb') as f:
        f.write(content)


def refresh_token_if_necessary():
    global g_spotify_token
    headers = {
        'Authorization': 'Basic {}'.format(BASE64_SPOTIFY_CLIENT_ID_SECRET),
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    try:
        form = {
            'grant_type': 'refresh_token',
            'refresh_token': SPOTIFY_REFRESH_TOKEN,
        }
        data_str = '&'.join(
            ['{}={}'.format(key, value) for key, value in form.items()])
        r = urequests.post(
            SPOTIFY_API_REFRESH_URL, data=data_str, headers=headers)
        result = r.json()
        g_spotify_token = result['access_token']
        return int(result['expires_in'])
    finally:
        r.close()


def get_current_playing_track():
    global g_spotify_token
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(g_spotify_token),
    }
    try:
        r = urequests.get(SPOTIFY_API_CURRENTLY_PLAYING_URL, headers=headers)

        if len(r.content) == 0:
            # if status code is 204, no track is played. It's not error
            if r.status_code == 204:
                return None
            else:  # warn about status_code
                lcd.println('header status is: {}'.format(r.status_code))
                return None
        return r.json()
    except Exception as e:
        lcd.println('Exception(get_current_playing_track): ' + str(e))
        lcd.println('Error: ' + str(r.content))
        raise e
    finally:
        r.close()


def get_image_url(track):
    if 'album' in track:
        album = track['album']
        if 'images' in album:
            images = album['images']
            for image in images:
                if image['width'] == 300:  # Only support 300x300 images
                    return image['url']
    return None


def download_image_to_file(image_url, filename, step_size=1024):
    r = urequests.get(image_url)
    try:
        with open(filename, 'wb') as f:
            while True:
                c = r.raw.read(step_size)
                if c:
                    f.write(c)
                else:
                    return
    except Exception as e:
        lcd.println('Exception(download_image): ' + str(e))
        raise e
    finally:
        r.close()


def download_image(image_url):
    try:
        r = urequests.get(image_url)
        write_file('tmp.jpg', r.content)
    except Exception as e:
        lcd.println('Exception(download_image): ' + str(e))
        raise e
    finally:
        r.close()


def show_image(file):
    lcd.clear()
    (screen_width, screen_height) = lcd.screensize()
    image_width = 300 / 2
    image_height = 300 / 2
    lcd.image(
        int((screen_width - image_width) / 2),
        int((screen_height - image_height) / 2),
        file,
        scale=1,
        type=lcd.JPG)


def print_title(track):
    lcd.setCursor(0, 0)
    lcd.println(track['name'])


def print_artist(track):
    artists = track['artists']
    artists_string = [a['name'] for a in artists]
    lcd.println(' By {}'.format(concatenate_and_strings(artists_string)))


def concatenate_and_strings(string_array):
    if len(string_array) == 0:
        return ''
    elif len(string_array) == 1:
        return string_array[0]
    else:
        command_concatenateds = ', '.join(string_array[:-1])
        return '{} and {}'.format(command_concatenateds, string_array[-1])


def task(expires_date):
    global g_track_id
    global g_track_img
    global g_showing_spotify_logo
    try:
        now = utime.time()
        if now > expires_date:
            next_expire_delta = refresh_token_if_necessary()
            expires_date = now + next_expire_delta
        track = get_current_playing_track()
        if track is not None:
            track_item = track['item']
            if track_item['id'] != g_track_id:
                image_url = get_image_url(track_item)
                lcd.clear()
                lcd.setCursor(0, 0)
                lcd.setColor(lcd.WHITE)
                if image_url and image_url != g_track_img:
                    download_image_to_file(image_url, 'tmp.jpg')
                    show_image('tmp.jpg')
                print_title(track_item)
                print_artist(track_item)
                g_track_id = track_item['id']
                g_track_img = image_url
                g_showing_spotify_logo = False
        else:
            if g_showing_spotify_logo is False:
                lcd.clear()
                show_image('spotify.jpg')
            g_showing_spotify_logo = True
        return expires_date
    except Exception as e:
        lcd.print('Exception(task): ' + str(e))
        import sys
        sys.print_exception(e)
        raise e


def main():
    try:
        lcd.println('main')
        if not connect_wifi(WIFI_CONFIG):
            lcd.println('Failed to connect')
            return
    except Exception as e:
        lcd.println(str(e))
        return
    expires_date = 0
    lcd.clear()
    lcd.setCursor(0, 0)
    while True:
        try:
            gc.collect()
            expires_date = task(expires_date)
            utime.sleep(10)
        except Exception as e:
            lcd.println('Exception(main): ' + str(e))
            import sys
            sys.print_exception(e)
            expires_date = 0  # Force to refresh key
            # anyway, retry connect
            connect_wifi(WIFI_CONFIG)


main()
