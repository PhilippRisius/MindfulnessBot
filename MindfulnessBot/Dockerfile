FROM python:3.7-alpine
WORKDIR /code
RUN apk add --no-cache gcc musl-dev linux-headers
RUN pip install datetime python-dotenv discord.py pymongo
EXPOSE 5000
COPY . .
CMD ["python", "./mindful_bot.py"]