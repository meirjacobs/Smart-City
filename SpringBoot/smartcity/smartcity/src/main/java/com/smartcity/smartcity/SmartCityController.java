package com.smartcity.smartcity;

import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.ui.Model;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;
import java.io.*;
import java.util.*;


@org.springframework.stereotype.Controller
public class SmartCityController {

    @GetMapping("/")
    public String getHomePage() {
        return "HomePage";
    }

    public class GetData {
        private String id;
        private String problemType;
        private String distance;
        private String latitude;
        private String longitude;
        private String problemDescription;
        private File image;
        private String status;
        private String startTime;
        private String endTime;

        public String getId() {
            return id;
        }

        public void setId(String id) {
            this.id = id;
        }

        public String getProblemType() {
            return problemType;
        }

        public void setProblemType(String problemType) {
            this.problemType = problemType;
        }

        public String getDistance() {
            return distance;
        }

        public void setDistance(String distance) {
            this.distance = distance;
        }

        public String getLatitude() {
            return latitude;
        }

        public void setLatitude(String latitude) {
            this.latitude = latitude;
        }

        public String getLongitude() {
            return longitude;
        }

        public void setLongitude(String longitude) {
            this.longitude = longitude;
        }

        public String getProblemDescription() {
            return problemDescription;
        }

        public void setProblemDescription(String problemDescription) {
            this.problemDescription = problemDescription;
        }

        public File getImage() {
            return image;
        }

        public void setImage(File image) {
            this.image = image;
        }

        public String getStatus() {
            return status;
        }

        public void setStatus(String status) {
            this.status = status;
        }

        public String getStartTime() {
            return startTime;
        }

        public void setStartTime(String startTime) {
            this.startTime = startTime;
        }

        public String getEndTime() {
            return endTime;
        }

        public void setEndTime(String endTime) {
            this.endTime = endTime;
        }
    }

    @PostMapping("/report")
    public String handleFileUpload(@RequestParam("image") MultipartFile file, @RequestParam("problemType") String problemType,
                                   @RequestParam("latitude") String latitude, @RequestParam("longitude") String longitude,
                                   @RequestParam("problemDescription") String problemDescription) throws IOException {
        System.out.println("You successfully uploaded " + file.getOriginalFilename() + "\nproblem type = " + problemType +
                "\nlatitude = " + latitude + "\nlongitude = " + longitude + "\nproblem description = " + problemDescription);
        WebClient client = WebClient.create("https://81ssn0783l.execute-api.us-east-1.amazonaws.com/deployedStage");
        WebClient.UriSpec<WebClient.RequestBodySpec> uriSpec = client.method(HttpMethod.POST);
        WebClient.RequestBodySpec bodySpec = uriSpec.uri("/");
        String bodyString = "{\"problem_type\":\""+problemType+"\",\"location\":["+latitude+","+longitude+"],\"problem_description\":\""+problemDescription+"\",\"image_path\":[\""+Base64.getEncoder().encodeToString(file.getBytes())+"\"]}";
        WebClient.RequestHeadersSpec<?> headersSpec = bodySpec.bodyValue(bodyString);
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
        resp.subscribe(System.out::println);
        return "ReportPage";
    }

    @PostMapping("/find")
    public String submitFind(@ModelAttribute("data") GetData body) {
        System.out.println("--FIND--");
        System.out.println("ID: " + body.getId());
        System.out.println("Problem Type: " + body.getProblemType());
        System.out.println("Problem Description: " + body.getProblemDescription());
        System.out.println("Distance: " + body.getDistance());
        System.out.println("Latitude: " + body.getLatitude());
        System.out.println("Longitude: " + body.getLongitude());
        System.out.println("Image: " + body.getImage());
        System.out.println("Status: " + body.getStatus());
        System.out.println("Start Time: " + body.getStartTime());
        System.out.println("End Time: " + body.getEndTime());

        MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<>();
        if (!body.getId().equals("0")) {
            queryParams.put("id", Arrays.asList(body.getId()));
        }
        if (!body.getProblemType().equals("Any")) {
            queryParams.put("problem_type", Arrays.asList(body.getProblemType()));
        }
        if (!body.getProblemDescription().equals("")) {
            queryParams.put("problem_description", Arrays.asList(body.getProblemDescription()));
        }
        if (!body.getDistance().equals("") && !body.getLatitude().equals("") && !body.getLongitude().equals("")) {
            queryParams.put("distance", Arrays.asList(body.getDistance()));
            queryParams.put("location", Arrays.asList(body.getLatitude() + "," + body.getLongitude()));
        }
        if (!body.getStatus().equals("Any")) {
            queryParams.put("current_status", Arrays.asList(body.getStatus()));
        }

        WebClient client = WebClient
                .builder()
                .baseUrl("https://81ssn0783l.execute-api.us-east-1.amazonaws.com/deployedStage")
                .build();
        List<String> types = Arrays.asList("id", "problem_type", "problem_description", "time_found", "current_status",
                "location", "image_path", "distance");
        List<String> results = client
                .get()
                .uri(uriBuilder -> uriBuilder
                        .path("/")
                        .queryParams(queryParams)
                        .build())
                .retrieve()
                .bodyToFlux(String.class)
                .collectList()
                .block();
        System.out.println(results);

        return "FindPage";
    }

    @GetMapping("/report")
    public String getReportPage(Model model) throws FileNotFoundException {
        return "ReportPage";
    }

    @GetMapping("/find")
    public String getFindPage(Model model) {
        model.addAttribute("data", new GetData());
        return "FindPage";
    }
}