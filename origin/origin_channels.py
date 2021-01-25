from multiprocessing import Process
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
import signal, sys, getopt, time, subprocess, shlex, os, shutil



class SIGINT_handler():
    def __init__(self):
        self.SIGINT = False

    def signal_handler(self, signal, frame):
        self.SIGINT = True


class OriginChannels():

    def __init__(self, fhdhr, origin):
        self.fhdhr = fhdhr
        self.origin = origin
        self.video_reference = {}
        self.fhdhr_dir = str(os.path.abspath(os.getcwd()))
        dcaps = DesiredCapabilities.CHROME
        dcaps["pageLoadStrategy"] = "none"    # Faster page loading / navigation
        prefs = {
            'credentials_enable_service': False,
            'profile': {
                'password_manager_enabled': False
             }
        }
        opts = webdriver.ChromeOptions()
        opts.add_argument("--disable-blink-features")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_experimental_option('prefs', prefs)
        opts.add_experimental_option("useAutomationExtension", False)
        opts.add_experimental_option("excludeSwitches", ['enable-automation'])
        self.driver = webdriver.Chrome(options = opts, desired_capabilities = dcaps)


    def check_auth(self, driver):
        # Check if authenticated
        try:
            logged_in = driver.find_element_by_xpath('//*[@id="icon"]')
            return driver   #Return driver only once authenticated
        except NoSuchElementException:
            # Authenticate Google
            google_auth = 'https://accounts.google.com/o/oauth2/v2/auth/oauthchooseaccount?redirect_uri=https%3A%2F%2Fdevelopers.google.com%2Foauthplayground&prompt=consent&response_type=code&client_id=407408718192.apps.googleusercontent.com&scope=email&access_type=offline&flowName=GeneralOAuthFlow'
            driver.get(google_auth)
            time.sleep(3)
            url = driver.current_url
            if 'AccountChooser' in url:
                try:
                    google_id = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "profileIdentifier")))
                    ActionChains(driver).move_to_element(google_id).click().perform()
                    time.sleep(1)
                except TimeoutException:
                    self.check_auth(driver)   #Retry
            if 'identifier' in url:
                try:
                    login_id = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "identifierId")))
                    username = self.fhdhr.config.dict["origin"]["username"]
                    login_id.send_keys(username)
                    login_id.send_keys(Keys.ENTER)
                    login_pass = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.NAME, "password")))
                    ActionChains(driver).move_to_element(login_pass).click().perform()
                    password = self.fhdhr.config.dict["origin"]["password"]
                    # Fix commas (,) in passwords
                    list_test = isinstance(password, list)
                    if str(list_test) == 'True':
                        password = ",".join(password)
                    login_pass.send_keys(password)
                    login_pass.send_keys(Keys.ENTER)
                    time.sleep(1)
                except TimeoutException:
                    self.check_auth(driver)   #Retry
            # Navigation: Login to YTTV
            url = 'https://tv.youtube.com/live'
            driver.get(url)
            time.sleep(1)
            try:   #Recheck auth
                logged_in = driver.find_element_by_xpath('//*[@id="icon"]')
                return driver
            except NoSuchElementException:
                try:
                    login = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "/html/body/header/div/div/a[2]")))
                    ActionChains(driver).move_to_element(login).click().perform()
                    google_id = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "profileIdentifier")))
                    ActionChains(driver).move_to_element(google_id).click().perform()
                    time.sleep(2)
                except TimeoutException:
                    self.check_auth(driver)   #Retry
                # Verify auth succesful
                driver.get('https://tv.youtube.com/live')
                time.sleep(1)
                self.check_auth(driver)    #Recheck auth


    def get_channels(self):
        driver = self.driver
        self.check_auth(driver)
        url = 'https://tv.youtube.com/live'
        driver.get(url)
        # Determine number of channels to scrape    
        stations = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="id-ytu-epg-section-rows"]/ytu-epg-row[1]/div/ytu-endpoint[1]/a/div'))) # Wait until first station has been listed
        stations = driver.find_elements_by_xpath('//*[@id="id-ytu-epg-section-rows"]/ytu-epg-row')
        stations = len(stations)
        # Scrape Live page
        channel_list = []
        station = 1
        while station <= stations:
            chan_element = driver.find_element_by_xpath('//*[@id="id-ytu-epg-section-rows"]/ytu-epg-row[' + str(station) + ']/div/ytu-endpoint[1]/a/ytu-img')
            callsign = str(chan_element.get_attribute("aria-label"))
            name = callsign
            chan_element = driver.find_element_by_xpath('//*[@id="id-ytu-epg-section-rows"]/ytu-epg-row[' + str(station) + ']/div/ytu-endpoint[1]/a/ytu-img/img')
            driver.execute_script("arguments[0].scrollIntoView();", chan_element)
            chan_img = str(chan_element.get_attribute("src"))
            chan_element = driver.find_element_by_xpath('//*[@id="id-ytu-epg-section-rows"]/ytu-epg-row[' + str(station) + ']/div/ytu-endpoint[2]/a')
            chan_url = str(chan_element.get_attribute("href"))
            try:
                video_id = str(chan_url.split('/')[4])
                clean_station_item = {
                                        "name": name,
                                        "callsign": callsign,
                                        "id": video_id,
                                        "thumbnail": chan_img
                                      }
                channel_list.append(clean_station_item)
            except IndexError:
                print("Error: No video id detected for " + str(name) + "!")
                print("  This channel will be skipped; please rescan later.")
            station += 1
        #driver.close()
        driver.get('https://www.google.com')
        return channel_list


    def get_channel_thumbnail(self, video_id):
        channel_list = self.get_channels()
        station_item = next((item for item in channel_list if item['id'] == video_id), None)
        chan_thumb = station_item.get("thumbnail","None")
        return chan_thumb


    def get_channel_stream(self, chandict):
        video_id = chandict["origin_id"]
        strm_port = self.fhdhr.config.dict["origin"]["stream_port"]
        #fhdhr_port = self.fhdhr.api.address_tuple[1]
        serv_host = subprocess.getoutput('hostname --fqdn')
        driver = self.driver
        self.check_auth(driver)
        # Start ffmpeg process, then monitoring log for connection closure
        tracker = Process(target=self.tuner_tracker, args=(video_id,driver))
        tracker.start()
        # Go to channel, and set up quality (if specified)
        url = 'https://tv.youtube.com/watch/' + video_id
        driver.get(url)
        driver = self.set_yttv_quality(driver)
        # Set up stream URL
        host_name = subprocess.getoutput('hostname --fqdn')
        serv_proto = 'http://'
        m3u8_manifest = '/manifest.m3u8'
        stream_url = str(serv_proto) + str(serv_host) + ':' + str(strm_port) + '/' + str(video_id) + str(m3u8_manifest)
        time.sleep(25)
        return stream_url


    def set_yttv_quality(self,driver):
        try:
            driver.maximize_window()
        except WebDriverException:
            driver.refresh()
        try:
            nav_bar = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="id-bottom-nav-bar"]')))
            ActionChains(driver).move_to_element(nav_bar).perform()
            # Set specific YTTV stream quality
            yttv_quality = self.fhdhr.config.dict["origin"]["yttv_quality"]
            try:
                if str(yttv_quality) != 'None':
                    settings_icon = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="id-player-settings"]/paper-icon-button[2]')))
                    ActionChains(driver).move_to_element(settings_icon).perform()
                    ActionChains(driver).click(settings_icon).perform()
                    quality_menu = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="id-ytu-cinema"]/div/div[6]/div/div/div/div[4]')))
                    ActionChains(driver).move_to_element(quality_menu).perform()
                    ActionChains(driver).click(quality_menu).perform()
                    time.sleep(1)
                    qual_text = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="id-ytu-cinema"]/div/div[6]/div/div/div[2]/div[1]')))   # Get value of highest quality choice
                    ActionChains(driver).move_to_element(qual_text).perform()
                    qual_text = qual_text.text
                    try:    # Remove 'HD' label, if present
                        qual_text = qual_text.split(' HD')[0]
                    except IndexError:
                        pass
                    print("Best quality: " + str(qual_text))
                    if str(qual_text) == '1080p60':
                        if str(yttv_quality) == '1080p60':
                            select_row = '1'
                        elif str(yttv_quality) == '720p60':
                            select_row = '2'
                        elif str(yttv_quality) == '480p':
                            select_row = '3'
                    elif str(qual_text) == '720p60':
                        if str(yttv_quality) == '1080p60':
                            select_row = '1'
                        elif str(yttv_quality) == '720p60':
                            select_row = '1'
                        elif str(yttv_quality) == '480p':
                            select_row = '2'
                    else:   # Select best available quality
                        select_row = '1'
                    if str(select_row) == '1':
                        quality_choice = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="id-ytu-cinema"]/div/div[6]/div/div/div[2]/div[1]')))
                    elif str(select_row) == '2':
                        quality_choice = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="id-ytu-cinema"]/div/div[6]/div/div/div[2]/div[2]')))
                    elif str(select_row) == '3':
                        quality_choice = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="id-ytu-cinema"]/div/div[6]/div/div/div[2]/div[3]')))
                    ActionChains(driver).move_to_element(quality_choice).perform()
                    ActionChains(driver).click(quality_choice).perform()
            except TimeoutException:
                print("Quality selection failed! - Timeout")
                self.set_yttv_quality(driver)   #Retry
            fullscreen = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="id-player-section"]/div/ytu-player-aux-controls/paper-icon-button[2]')))
            ActionChains(driver).move_to_element(fullscreen).click().perform()
        except StaleElementReferenceException:
            self.set_yttv_quality(driver)   #Retry
        player_area = driver.find_element_by_xpath('//*[@id="id-ytu-cinema"]/div/div[2]')
        ActionChains(driver).move_to_element(player_area).perform()
        return driver


    def make_stream(self,stream_dir):
        # Get environment values
        sound_card = subprocess.getoutput('pactl list sources | grep -m 1 -B 1 "Description: Monitor of" | grep "Name:" | cut -d " " -f 2')
        display_num = subprocess.getoutput('echo $DISPLAY')
        display_size = subprocess.getoutput('xdpyinfo | grep dimensions | cut -d ":" -f 2 | cut -d "p" -f 1')
        display_size = display_size.lstrip()
        # Pull desired ffmpeg parameters
        r_value = self.fhdhr.config.dict["origin"]["ffmpeg_fps"]
        crf_value = self.fhdhr.config.dict["origin"]["ffmpeg_quality"]
        a_delay = self.fhdhr.config.dict["origin"]["audio_delay"]
        # Move to stream directory
        os.chdir(str(stream_dir))
        if str(self.fhdhr.config.dict["origin"]["yttv_quality"]) != 'None':
            time.sleep(8)   #Add delay for quality selection routine
        time.sleep(10)
        # Set ffmpeg command string
        ffmpeg_stream = 'ffmpeg -y -f x11grab -s ' + str(display_size) + ' -r ' + str(r_value) + ' -thread_queue_size 4096 -i ' + str(display_num) + '.0+nomouse -f pulse -ac 2 -thread_queue_size 4096 -i ' + str(sound_card) + ' -c:v libx264 -crf ' + str(crf_value) + ' -preset ultrafast -pix_fmt yuv420p -tune zerolatency -c:a aac -strict experimental -b:a 128k -ar 44100 -filter_complex "[1:a] adelay=' + str(a_delay) + '|' + str(a_delay) + ' [delayed_audio]" -map 0:v -map [delayed_audio] -f hls -hls_time 4 -hls_segment_type "mpegts" -hls_list_size 10 -hls_delete_threshold 20 -hls_flags "delete_segments+program_date_time+temp_file" -master_pl_name "manifest.m3u8" -hls_segment_filename "segment_%v_%03d.ts" "manifest_%v.m3u8"'
        ffmpeg_stream = str(ffmpeg_stream)
        # Start streaming process
        ffmpeg_args = shlex.split(ffmpeg_stream)
        ffmpeg_proc = subprocess.Popen(ffmpeg_args)
        return None


    def tuner_tracker(self,video_id,driver):
        handler = SIGINT_handler()
        signal.signal(signal.SIGINT, handler.signal_handler)
        # Make stream directory
        stream_dir = str(self.fhdhr_dir) + '/origin/www_dir/' + str(video_id)
        try:
            os.mkdir(str(stream_dir))
        except OSError:
            pass
        mkstream = Process(target=self.make_stream, args=(stream_dir,))
        mkstream.start()
        # Move to log directory
        log_dir = str(self.fhdhr_dir) + '/data/cache/logs'
        os.chdir(str(log_dir))
        # Set stream initiation time
        stream_init_time = time.localtime()
        stream_init_time = time.strftime("%Y/%m/%d %H:%M:%S", stream_init_time)
        stream_end_time = stream_init_time
        # Run until connection closed; force exit on SIGINT
        print("Tracking log file for connection closure...")
        while stream_end_time <= stream_init_time:
            stream_end_time = subprocess.getoutput('grep "Connection Closed." ./fHDHR.log | tail -1 | cut -d "," -f 1')
            stream_end_time = stream_end_time.replace("-", "/")
            time.sleep(1)
            if handler.SIGINT:
                print("Termination signal caught...")
                stream_init_time = '1900/01/01 00:00:01'
        print("Terminating streamer processes...")
        # Clean up working stream directory and files (also kills ffmpeg)
        try:
            shutil.rmtree(str(stream_dir))
        except OSError as e:
            print("Error: %s : %s" % (str(stream_dir), e.strerror))
        # Redirect driver to inactive page
        driver.get('https://www.google.com')
        return None



