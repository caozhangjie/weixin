FROM python:2.7-onbuild

RUN chmod 777 ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]

CMD ["uwsgi", "--ini", "uwsgi.ini"]