from enum import Enum


class Commands(Enum):
    """ start """
    start = ["начать"]

    """ link to jobs """
    jobs = ["вакансии", "стажировки", "практики"]

    """ link to career """
    career = ["профориентация"]

    """ Career tips """
    career_tips = ["карьерные советы"]

    """ greetings """
    greetings = ["привет", "здравствуйте"]

    """ help """
    help = ["помощь", "меню", "команды", "справка", "кнопки"]

    """ administrator """
    admin = ["/admin2022load"]

    """ exit """
    exit = ["пока 2020"]
