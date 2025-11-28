from database import drop_tables, clear_all_data, get_engine
import sys

def main():
    if len(sys.argv) > 1:
        command = sys.argv[1]
        engine = get_engine()
        
        if command == "drop":
            confirm = input("Вы уверены, что хотите удалить все таблицы? (y/n): ")
            if confirm.lower() == 'y':
                drop_tables(engine)
            else:
                print("Операция отменена")
                
        elif command == "clear":
            confirm = input("Вы уверены, что хотите очистить все данные? (y/n): ")
            if confirm.lower() == 'y':
                clear_all_data(engine)
            else:
                print("Операция отменена")
                
        elif command == "reset":
            confirm = input("Вы уверены, что хотите полностью сбросить базу данных? (y/n): ")
            if confirm.lower() == 'y':
                drop_tables(engine)
                from database import create_tables
                create_tables(engine)
                print("База данных полностью сброшена")
            else:
                print("Операция отменена")
        else:
            print("Неизвестная команда. Используйте: drop, clear или reset")
    else:
        print("Использование: python cleanup.py [command]")
        print("Команды:")
        print("  drop  - удалить все таблицы")
        print("  clear - очистить все данные (без удаления таблиц)")
        print("  reset - полный сброс базы данных")

if __name__ == "__main__":
    main()