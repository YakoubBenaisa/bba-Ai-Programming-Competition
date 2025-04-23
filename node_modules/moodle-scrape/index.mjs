"use strict";

import fetch from 'node-fetch';
import * as cheerio from 'cheerio';

export class Moodle {
	constructor(url) {
		this.url = url;
		this.cookies = null;
	}
	async login(username, password) {
		const form = new URLSearchParams();
		form.append('username', username);
		form.append('password', password);

		let res = await fetch(this.url);
		const body = await res.text();
		const $ = cheerio.load(body);
		form.append('logintoken', $("[name='logintoken']")[0].attribs.value);
	
		res = await fetch(`${this.url}/login/index.php`, {
			headers: { 'cookie': res.headers.raw()['set-cookie'].find(c => c.startsWith("MoodleSession")) },
			method: 'POST',
			body: form,
			redirect: 'manual'
		});
	
		this.cookies = res.headers.raw()['set-cookie'].find(c => c.startsWith("MoodleSession"));
		return this.cookies;
	}
	async getInfo(cookies = this.cookies) {
		const res = await fetch(`${this.url}/calendar/view.php?view=upcoming`, {
			headers: { 'cookie': cookies }
		});
		const body = await res.text();
		const $ = cheerio.load(body);
	
		let tasks;
		try {
			tasks = $('.calendar_event_course .name').map(function (i, el) {
				try {
					return {
						name: el.children[0].data,
						description: $($('.description').get(i)).find('b')[0].children[0].data,
						deadline: $($('.description').get(i)).children().first().children().get(1).children[0].children[0].data + $($('.description').get(i)).children().first().children().get(1).children[1].data,
						course: $($('.description').get(i)).children().last().children().get(1).children[0].children[0].data
					};
				} catch { return null; }
			}).toArray();
		} catch {
			tasks = null;
		}
		
		try {
			return {
				name: $(".usertext")[0].children[0].data,
				courses: $("#main-header .visible1 > a").map(function (_, el) {
					return el.attribs.title
				}).toArray(),
				tasks: tasks
			};
		} catch {
			return null;
		}
	}
}