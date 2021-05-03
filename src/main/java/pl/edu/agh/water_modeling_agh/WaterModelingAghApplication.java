package pl.edu.agh.water_modeling_agh;

import io.kubernetes.client.openapi.ApiException;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

import java.io.IOException;

@SpringBootApplication
public class WaterModelingAghApplication {

	public static void main(String[] args) {
		SpringApplication.run(WaterModelingAghApplication.class, args);
	}

}
