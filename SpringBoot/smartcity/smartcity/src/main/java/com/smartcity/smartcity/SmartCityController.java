package com.smartcity.smartcity;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.json.JsonParserFactory;
import org.springframework.core.env.Environment;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.ui.Model;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;
import reactor.core.publisher.Mono;
import java.io.*;
import java.util.*;


@org.springframework.stereotype.Controller
public class SmartCityController {

    @Autowired
    private Environment env;

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
    public String handleFileUpload(@RequestParam("image") MultipartFile[] files, @RequestParam("problemType") String problemType,
                                   @RequestParam("latitude") String latitude, @RequestParam("longitude") String longitude,
                                   @RequestParam("problemDescription") String problemDescription) throws IOException {
        WebClient client = WebClient.create(env.getProperty("apiURL"));
        WebClient.UriSpec<WebClient.RequestBodySpec> uriSpec = client.method(HttpMethod.POST);
        WebClient.RequestBodySpec bodySpec = uriSpec.uri("/");
        StringBuilder fileString = new StringBuilder();
        for (int i = 0; i < files.length; i++) {
            fileString.append("\"");
            fileString.append(Base64.getEncoder().encodeToString(files[i].getBytes()));
            fileString.append("\"");
            if (files.length != 1 && i != files.length - 1) {
                fileString.append(",");
            }
        }
        String bodyString = "{\"problem_type\":\""+problemType+"\",\"location\":["+latitude+","+longitude+"],\"problem_description\":\""+problemDescription+"\",\"image_path\":["+fileString+"]}";
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
        return "ThankYouPage";
    }

    @PostMapping("/find")
    public String submitFind(@ModelAttribute("data") GetData body, RedirectAttributes redirectAttributes) {
        /*System.out.println("--FIND--");
        System.out.println("ID: " + body.getId());
        System.out.println("Problem Type: " + body.getProblemType());
        System.out.println("Problem Description: " + body.getProblemDescription());
        System.out.println("Distance: " + body.getDistance());
        System.out.println("Latitude: " + body.getLatitude());
        System.out.println("Longitude: " + body.getLongitude());
        System.out.println("Image: " + body.getImage());
        System.out.println("Status: " + body.getStatus());
        System.out.println("Start Time: " + body.getStartTime());
        System.out.println("End Time: " + body.getEndTime());*/

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
                .baseUrl(env.getProperty("apiURL"))
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
        redirectAttributes.addFlashAttribute("message", results);
        //System.out.println(results);

        return "redirect:/results";
    }

    @GetMapping("/results")
    public String getResultsPage(/*@ModelAttribute("message") String message*/) {
        return "SearchResults";
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

    @GetMapping("/thanks")
    public String getThanksPage() {
        return "ThankYouPage";
    }
}