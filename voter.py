from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Voter:

    MAX_RETRIES = 3
    MAX_RATING_VALUE = 5.0
    MIN_RATING_VALUE = 1.0

    def __init__(self, driver_path: str) -> None:
        self.driver_path = driver_path
        self.target = ""
        self._setup_driver()
    
    def __del__(self):
        self.driver.close()

    def open(self, target: str = "", dismiss_cookies: bool = False) -> bool:
        self.target = target
        try:
            url = "https://www.polskieskarby.pl/szlak-kulinarny/trojmiasto"
            if target:
                self.driver.get("{}/restauracja-{}".format(url, target))
            else:
                self.driver.get(url)
        except WebDriverException as err:
            Voter._print("Page not loaded: {}".format(str(err)))
            return False

        if dismiss_cookies:
            try:
                cookies_dismiss = self.driver.find_element(by=By.CLASS_NAME, value="cookies-action")
                cookies_dismiss.click()
            except WebDriverException as err:
                Voter._print("Missing cookies popup, cache not cleared? - {}".format(str(err)))
                return False

        return True
    
    def vote(self, stars: int) -> float:
        assert stars in range(int(Voter.MIN_RATING_VALUE), int(Voter.MAX_RATING_VALUE) + 1)
        attempt = 0
        while attempt < Voter.MAX_RETRIES:
            try:
                return self._vote(stars)
            except Exception as err:
                Voter._print("Exception: {}".format(str(err)))
                self.setup_driver()
                self.open(self.target)
                attempt += 1
        return 0.0
    
    def _setup_driver(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_argument("--headless")
        options.add_argument("--log-level=3")
        self.driver = webdriver.Chrome(self.driver_path, options=options)
        self.driver.delete_all_cookies()
        self.driver.implicitly_wait(30)        
    
    def _vote(self, stars: int) -> float:
        if not self._confirm_no_vote_cast():
            raise Exception("Intial state indicates vote cast already")

        rate_wrap_outer = self.driver.find_element(by=By.CLASS_NAME, value="rate")
        rate_wrap_inner = rate_wrap_outer.find_element(by=By.CLASS_NAME, value="element-relative")
        rate_stars = rate_wrap_inner.find_elements(by=By.CLASS_NAME, value="rate-star")
        if len(rate_stars) != 5:
            raise Exception("Incorrect star count {} instead of 5".format(len(rate_stars)))

        rate_stars[stars - 1].click()
        if not self._confirm_vote_cast():
            raise Exception("Final state indicates no vote cast")

        rating = self._get_rating()
        if rating < 1.0 or rating > 5.0:
            raise Exception("Invalid rating value received: {}".format(rating))
        return rating

    def _confirm_no_vote_cast(self) -> bool:
        try:
            rate_title = self.driver.find_element(by=By.CLASS_NAME, value="restaurant-details-rate-title")
            return "Oceń restaurację" in rate_title.get_attribute("innerHTML")
        except WebDriverException:
            return False

    def _confirm_vote_cast(self) -> bool:
        try:
            self._wait_for_vote_animation()
            rate_locked = self.driver.find_element(by=By.CLASS_NAME, value="restaurant-details-rate-locked")
            return "Dziękujemy za oddany głos!" in rate_locked.get_attribute("innerHTML")
        except WebDriverException:
            return False
    
    def _get_rating(self) -> float:
        try:
            self._wait_for_vote_animation()
            rating_wrap = self.driver.find_element(by=By.CLASS_NAME, value="rate-average-value")
            rating = rating_wrap.get_attribute("innerHTML").replace(",", ".")
            return float(rating)
        except WebDriverException:
            return 0.0
        except ValueError:
            return 0.0
    
    def _wait_for_vote_animation(self):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "restaurant-details-rate-locked")
            )
        )

    def _print(msg) -> None:
        print("[Voter] {}".format(msg))
