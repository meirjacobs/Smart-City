package com.smartcity.smartcity;

import org.apache.tomcat.util.http.fileupload.FileUtils;
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
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalDate;
import java.util.Base64;
import java.util.Scanner;

@org.springframework.stereotype.Controller
public class SmartCityController {
    //@GetMapping("/greeting")
    @GetMapping("/")
    public String getHomePage(/*@RequestParam(name="name", required=false, defaultValue="Anonymous Dude") String name, Model model*/) {
        //model.addAttribute("name", name);
        return "HomePage";
    }

    public class PostData {
        private String problemType;
        private String latitude;
        private String longitude;
        private String problemDescription;
        private File encodedImage;

        public String getProblemType() {
            return problemType;
        }

        public void setProblemType(String problemType) {
            this.problemType = problemType;
        }

        public String getLongitude() {
            return longitude;
        }

        public void setLongitude(String longitude) {
            this.longitude = longitude;
        }

        public String getLatitude() {
            return latitude;
        }

        public void setLatitude(String latitude) {
            this.latitude = latitude;
        }

        public File getEncodedImage() {
            return encodedImage;
        }

        public void setEncoded_image(File encodedImage) {
            this.encodedImage = encodedImage;
        }

        public String getProblemDescription() {
            return problemDescription;
        }

        public void setProblemDescription(String problemDescription) {
            this.problemDescription = problemDescription;
        }
    }

    @PostMapping("/report")
    public String showPage(@ModelAttribute("data") PostData body) throws IOException {

        System.out.println("Problem Type: " + body.getProblemType());
        System.out.println("Problem Description: " + body.getProblemDescription());
        System.out.println("Latitude: " + body.getLatitude());
        System.out.println("Longitude: " + body.getLongitude());
        /*byte[] fileContent = Files.readAllBytes(body.getEncodedImage().toPath());
        String encodedString = Base64
                .getEncoder()
                .encodeToString(fileContent);
        System.out.println("Image: " + encodedString);*/
        System.out.println("Encoded Image: " + body.getEncodedImage());
        return "ReportPage";
    }

    @GetMapping("/report")
    public String getReportPage(Model model) throws FileNotFoundException {
        model.addAttribute("data", new PostData()); //assume SomeBean has a property called datePlanted

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