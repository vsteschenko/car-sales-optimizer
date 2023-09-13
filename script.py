#!/usr/bin/env python3

import json
import locale
import sys
import emails
import os
import os.path
import reports
import requests
import email.message
import mimetypes
import smtplib

def load_data(filename):
	"""Loads the contents of filename as a JSON file."""
	with open(filename) as json_file:
		data = json.load(json_file)
	return data

max_sales = {'total_sales': 0}
max_car_year = {}

def format_car(car):
	"""Given a car dictionary, returns a nicely formatted name."""
	return "{} {} ({})".format(
		car["car_make"], car["car_model"], car["car_year"])

def process_data(data):
	"""Analyzes the data, looking for maximums.

	Returns a list of lines that summarize the information.
	"""
	max_revenue = {"revenue": 0}
	max_sales = {"total_sales": 0}
	max_car_year = {}

	for item in data:
		# Calculate the revenue generated by this model (price * total_sales)
		# We need to convert the price from "$1234.56" to 1234.56
		item_price = locale.atof(item["price"].strip("$"))
		item_revenue = item["total_sales"] * item_price
		if item_revenue > max_revenue["revenue"]:
			item["revenue"] = item_revenue
			max_revenue = item
		if item["total_sales"] > max_sales["total_sales"]:
			max_sales = item
		if item["car"]["car_year"] in max_car_year:
			max_car_year[item["car"]["car_year"]] += item["total_sales"]
		else:
			max_car_year[item["car"]["car_year"]] = item["total_sales"]
	most_popular_car_year = max(max_car_year, key=max_car_year.get)

	summary = [
		"The {} generated the most revenue: ${}".format(
			format_car(max_revenue["car"]), max_revenue["revenue"]),
		"The {} had the most sales: {}".format(
			format_car(max_sales["car"]), max_sales["total_sales"]),
		"The most popular car year was {}: {} sales".format(
			most_popular_car_year, max_car_year[most_popular_car_year])
	]

	return summary

def cars_dict_to_table(car_data):
	"""Turns the data in car_data into a list of lists."""
	car_data.sort(key=lambda x: x["total_sales"], reverse=True)
	table_data = [["ID", "Car", "Price", "Total Sales"]]
	for item in car_data:
		table_data.append([item["id"], format_car(item["car"]), item["price"], item["total_sales"]])
	return table_data

def generate(sender, recipient, subject, body, pdf_file_path):
	message = email.message.EmailMessage()
	message["From"] = sender
	message["To"] = recipient
	message["Subject"] = subject
	message.set_content(body)

	attachment_filename = os.path.basename(pdf_file_path)
	mime_type, _ = mimetypes.guess_type(pdf_file_path)
	mime_type, mime_subtype = mime_type.split('/', 1)

	with open(attachment_path, 'rb') as ap:
		message.add_attachment(ap.read(),
							  maintype=mime_type,
							  subtype=mime_subtype,
							  filename=attachment_filename)
	return message

def send(message):
	mail_server = smtplib.SMTP('localhost')
	mail_server.send_message(message)
	mail_server.quit()

def main(argv):
	"""Process the JSON data and generate a full report out of it."""
	data = load_data("car_sales.json")
	summary = process_data(data)
	print(summary)
	pdf_file_path = ""
	table_data = cars_dict_to_table(data)
	reports.generate(pdf_file_path, "Sales summary", "<br/>".join(summary), table_data)
	sender = ""
	recipient = ""
	subject = "Sales summary for last month"
	body = "The same summary from the PDF, but using \n between the lines"
	message = emails.generate(sender, recipient, subject, body, pdf_file_path)
	emails.send(message)

if __name__ == "__main__":
	main(sys.argv)

