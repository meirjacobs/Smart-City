package com.smartcity.smartcity;

import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.io.File;
import java.io.FileNotFoundException;
import java.time.LocalDate;
import java.util.Scanner;

@org.springframework.stereotype.Controller
public class SmartCityController {
    //@GetMapping("/greeting")
    @GetMapping("/")
    public String getHomePage(/*@RequestParam(name="name", required=false, defaultValue="Anonymous Dude") String name, Model model*/) {
        //model.addAttribute("name", name);
        return "HomePage";
    }

    public class ReportData {
        private String body;

        public void setData(String bodyTxt) {
            body = bodyTxt;
        }

        public String getData() {
            return body;
        }
    }

    @PostMapping("/report")
    public String showPage(@ModelAttribute("data") ReportData body) {

        System.out.println("Data: " + body.getData()); //in reality, you'd use a logger instead :)
        return "ReportPage";
    }

    @GetMapping("/report")
    public String getReportPage(Model model) throws FileNotFoundException {
        model.addAttribute("data", new ReportData()); //assume SomeBean has a property called datePlanted

        /*WebClient client = WebClient.create("https://x1vj5n9ki4.execute-api.us-east-1.amazonaws.com/deployedStage");
        WebClient.UriSpec<WebClient.RequestBodySpec> uriSpec = client.method(HttpMethod.POST);
        WebClient.RequestBodySpec bodySpec = uriSpec.uri("/");
        File file = new File("C:\\Users\\17324\\Downloads\\smartcity\\smartcity\\src\\main\\java\\com\\smartcity\\smartcity\\PostBody.txt");
        Scanner scanner = new Scanner(file);
        StringBuilder s = new StringBuilder();
        while (scanner.hasNextLine()) {
            s.append(scanner.nextLine());
        }
        WebClient.RequestHeadersSpec<?> headersSpec = bodySpec.bodyValue(s.toString());
        //Mono<String> response = headersSpec.retrieve().bodyToMono(String.class);
        Mono<String> resp = headersSpec.exchangeToMono(response -> {
            if (response.statusCode()
                    .equals(HttpStatus.OK)) {
                return response.bodyToMono(String.class);
            } else if (response.statusCode()
                    .is4xxClientError()) {
                return Mono.just("Error response");
            } else {
                return response.createException()
                        .flatMap(Mono::error);
            }
        });
        resp.subscribe(System.out::println);*/
        return "ReportPage";
    }

    @GetMapping("/find")
    public String getFindPage() {
        return "FindPage";
    }
}