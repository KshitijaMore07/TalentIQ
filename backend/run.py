from config import Config

if not Config.USE_SQLITE:  # create the MySQL database on first run
    import pymysql
    m = Config.MYSQL
    try:
        c = pymysql.connect(host=m["host"], port=m["port"], user=m["user"], password=m["password"])
        c.cursor().execute(f"CREATE DATABASE IF NOT EXISTS `{m['db']}` CHARACTER SET utf8mb4")
        c.commit(); c.close()
    except Exception as e:
        print("Could not reach MySQL:", e)

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
