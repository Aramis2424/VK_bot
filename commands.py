from enum import Enum


class Commands(Enum):
    """ start """
    start = ["начать"]

    """ link to jobs """
    jobs = ["вакансии", "стажировки", "практики"]

    """ link to career """
    career = ["Профориентация"]

    """ greetings """
    greetings = ["привет", "здравствуйте"]

    """ help """
    help = ["помощь", "меню", "команды", "справка", "кнопки"]

    """ send message to administrator """
    admin = ["Написать администратору группы"]

    """ exit """
    exit = ["пока 2020"]
