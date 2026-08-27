package test

import (
	"testing"
	"github.com/gruntwork-io/terratest/modules/docker"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestDockerBuild(t *testing.T) {
	t.Parallel()

	options := &docker.BuildOptions{
		Tags:         []string{"test-backend:latest"},
		Target:       "production",
		ContextDir:   "../../exercise-1.1/backend",
	}

	docker.Build(t, options, "../../exercise-1.1/backend")

	imageId := docker.GetImageId(t, "test-backend:latest")
	require.NotEmpty(t, imageId)
	assert.Contains(t, imageId, "sha256:")
}

func TestDockerRun(t *testing.T) {
	t.Parallel()

	container := docker.RunAndGetID(t, &docker.RunOptions{
		ImageName: "test-backend:latest",
		Detach:    true,
		EnvironmentVariables: []string{
			"DATABASE_URL=postgresql://test:test@localhost:5432/testdb",
		},
	})

	defer docker.Stop(t, container)

	output := docker.Exec(t, container, []string{"curl", "-s", "http://localhost:5000/api/health"})
	assert.Contains(t, output, "healthy")
}

func TestDockerImageSize(t *testing.T) {
	t.Parallel()

	options := &docker.BuildOptions{
		Tags:         []string{"test-backend:latest"},
		Target:       "production",
		ContextDir:   "../../exercise-1.1/backend",
	}

	docker.Build(t, options, "../../exercise-1.1/backend")

	inspectOutput := docker.Inspect(t, "test-backend:latest")
	require.NotNil(t, inspectOutput)

	size := inspectOutput.Size
	assert.Less(t, size, int64(500*1024*1024), "Image size should be less than 500MB")
}
