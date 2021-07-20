package com.smartcity.smartcity;

import org.apache.tomcat.util.http.fileupload.FileUtils;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.ClientResponse;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.Base64;
import java.util.List;
import java.util.Scanner;

import static org.apache.commons.io.FileUtils.readFileToByteArray;
import static org.apache.tomcat.util.http.fileupload.FileUtils.*;

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
        //private File image;
        //private byte[] image;
        //private byte[] image;
        private String image;

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

        /*public File getImage() {
            //System.out.println(image.getAbsolutePath());
            return image;
        }

        public void setImage(File image) {
            this.image = image;
        }*/

        /*public byte[] getImage() {
            //System.out.println(image.getAbsolutePath());
            return image;
        }

        public void setImage(byte[] image) {
            System.out.println(Arrays.toString(image));
            this.image = image;
        }*/
        /*public byte[] getImage() {
            //System.out.println(image.getAbsolutePath());
            return image;
        }

        public void setImage(MultipartFile image) throws IOException {
            //System.out.println(Arrays.toString(image));
            this.image = Base64.getEncoder().encode(image.getBytes());
        }*/

        public String getImage() throws IOException {
            File imageFile = new File(image);
            byte[] fileContent = Files.readAllBytes(imageFile.toPath());
            return Base64.getEncoder().encodeToString(fileContent);
            //return image;
        }

        public void setImage(String image)  {
            this.image = image;
        }

        public String getProblemDescription() {
            return problemDescription;
        }

        public void setProblemDescription(String problemDescription) {
            this.problemDescription = problemDescription;
        }
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
    public String submitReport(@ModelAttribute("data") PostData body) throws IOException {
        System.out.println("--REPORT--");
        System.out.println("Problem Type: " + body.getProblemType());
        System.out.println("Problem Description: " + body.getProblemDescription());
        System.out.println("Latitude: " + body.getLatitude());
        System.out.println("Longitude: " + body.getLongitude());

        System.out.println("Image Path: [very long stuff that will fill up the whole console]" /*+ body.getImage()*/);
        // System.out.println("Encoded image: " + Arrays.toString(body.getImage()));
        //String encodedString =
        //System.out.println(Base64.getEncoder().encode(body.getImage()));
        //System.out.println("Encoded Image: " + );

        WebClient client = WebClient.create("https://81ssn0783l.execute-api.us-east-1.amazonaws.com/deployedStage");
        WebClient.UriSpec<WebClient.RequestBodySpec> uriSpec = client.method(HttpMethod.POST);
        WebClient.RequestBodySpec bodySpec = uriSpec.uri("/");
        String bodyString = "{\"problem_type\":\""+body.getProblemType()+"\",\"location\":["+body.getLatitude()+","+body.getLongitude()+"],\"problem_description\":\""+body.getProblemDescription()+"\",\"image_path\":[\""+body.getImage()+"\"]}";
        //System.out.println(bodyString);
        WebClient.RequestHeadersSpec<?> headersSpec = bodySpec.bodyValue(bodyString);
        //Mono<String> response = headersSpec.retrieve().bodyToMono(String.class);
        Mono<String> resp = headersSpec.exchangeToMono(response -> {
            if (response.statusCode()
                    .equals(HttpStatus.OK)) {
                //System.out.println(">>>>" + response.bodyToMono(String.class));
                return response.bodyToMono(String.class);
            } else if (response.statusCode()
                    .is4xxClientError()) {
                return Mono.just("Error response");
            } else {
                return response.createException()
                        .flatMap(Mono::error);
            }
            //return response.bodyToMono(String.class);
        });
        resp.subscribe(System.out::println);
        //byte[] fileContent = Files.readAllBytes(body.getImage());
        /*byte[] fileContent = readFileToByteArray(body.getImage());
        String encodedString = Base64
                .getEncoder()
                .encodeToString(fileContent);
        System.out.println("Image: " + encodedString);*/
        /*Reader fileReader = new FileReader(body.getImage());
        int data = fileReader.read();
        while(data != -1) {
            //do something with data...
            System.out.println("Data :" + data);

            data = fileReader.read();
        }
        fileReader.close();*/
        //System.out.println("Image: " + body.getImage());
        //System.out.println("Encoded Image: " + body.getImage().getOriginalFilename());
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

        //WebClient.create("https://81ssn0783l.execute-api.us-east-1.amazonaws.com/deployedStage")
        /*Mono<String> resp = WebClient.create().get()
                .uri(builder -> builder/*.scheme("https")*/
                        /*.host("https://81ssn0783l.execute-api.us-east-1.amazonaws.com/deployedStage").path("/")
                        .queryParam("id", "1")
                        .build())
                .retrieve()
                .bodyToMono(String.class);
        resp.subscribe(System.out::println);*/

        /*WebClient client = WebClient.create("https://81ssn0783l.execute-api.us-east-1.amazonaws.com/deployedStage");
        WebClient.UriSpec<WebClient.RequestBodySpec> uriSpec = client.method(HttpMethod.GET);
        WebClient.RequestBodySpec bodySpec = uriSpec.uri("/");*/
        /*File file = new File("C:\\Users\\17324\\Downloads\\smartcity\\smartcity\\src\\main\\java\\com\\smartcity\\smartcity\\PostBody.txt");
        Scanner scanner = new Scanner(file);
        StringBuilder s = new StringBuilder();
        while (scanner.hasNextLine()) {
            s.append(scanner.nextLine());
        }
        WebClient.RequestHeadersSpec<?> headersSpec = bodySpec.bodyValue(s.toString());*/
        //Mono<String> response = headersSpec.retrieve().bodyToMono(String.class);
        //WebClient.RequestHeadersSpec<?> headersSpec = bodySpec.bodyValue("{\"id\":\"1\"}");
        /*WebClient.RequestHeadersSpec<?> headersSpec = bodySpec.bodyValue("id=1");
        Mono<String> resp = headersSpec.exchangeToMono(response -> {
            return response.bodyToMono(String.class);
                }
            /*if (response.statusCode()
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
        return "FindPage";
    }

    @GetMapping("/report")
    public String getReportPage(Model model) throws FileNotFoundException {
        model.addAttribute("data", new PostData());

//        WebClient client = WebClient.create("https://81ssn0783l.execute-api.us-east-1.amazonaws.com/deployedStage");
//        WebClient.UriSpec<WebClient.RequestBodySpec> uriSpec = client.method(HttpMethod.POST);
//        WebClient.RequestBodySpec bodySpec = uriSpec.uri("/");
//        File file = new File("C:\\Users\\17324\\Downloads\\smartcity\\smartcity\\src\\main\\java\\com\\smartcity\\smartcity\\PostBody.txt");
//        Scanner scanner = new Scanner(file);
//        StringBuilder s = new StringBuilder();
//        while (scanner.hasNextLine()) {
//            s.append(scanner.nextLine());
//        }
//        WebClient.RequestHeadersSpec<?> headersSpec = bodySpec.bodyValue(s.toString());
//        //Mono<String> response = headersSpec.retrieve().bodyToMono(String.class);
//        Mono<String> resp = headersSpec.exchangeToMono(response -> {
//            if (response.statusCode()
//                    .equals(HttpStatus.OK)) {
//                //System.out.println(">>>>" + response.bodyToMono(String.class));
//                return response.bodyToMono(String.class);
//            } else if (response.statusCode()
//                    .is4xxClientError()) {
//                return Mono.just("Error response");
//            } else {
//                return response.createException()
//                        .flatMap(Mono::error);
//            }
//        });
//        resp.subscribe(System.out::println);
        return "ReportPage";
    }

    @GetMapping("/find")
    public String getFindPage(Model model) {
        model.addAttribute("data", new GetData());
        return "FindPage";
    }
}