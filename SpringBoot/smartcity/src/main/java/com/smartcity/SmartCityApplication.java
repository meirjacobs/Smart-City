package com.smartcity;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

import java.util.Map;

@SpringBootApplication
public class SmartCityApplication {

	public static void main(String[] args) {
		/*Map<String, String> map = System.getenv();
		for (Map.Entry <String, String> entry: map.entrySet()) {
			System.out.println("Variable Name:- " + entry.getKey() + " Value:- " + entry.getValue());
		}*/
		SpringApplication.run(SmartCityApplication.class, args);
	}

}
